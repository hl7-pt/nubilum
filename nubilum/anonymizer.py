"""HL7 Message Anonymization Module."""

import re
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Set
import logging

logger = logging.getLogger(__name__)


class HL7Anonymizer:
    """Anonymizes HL7 v2 messages while preserving structure."""

    # Common Portuguese first names for pseudo-generation
    FIRST_NAMES = [
        "Patient", "Test", "Sample", "Demo", "Example",
        "Anonymous", "Unknown", "John", "Jane", "Person"
    ]

    LAST_NAMES = [
        "Doe", "Smith", "Test", "Sample", "Anonymous",
        "Person", "User", "Patient", "Example", "Demo"
    ]

    def __init__(self):
        """Initialize the anonymizer."""
        self.processed_ids: Dict[str, str] = {}
        self.processed_names: Dict[str, str] = {}

    def _generate_pseudo_id(self, original: str, prefix: str = "ID") -> str:
        """Generate a consistent pseudo ID based on the original."""
        if not original or original.strip() == "":
            return f"{prefix}000000"

        if original in self.processed_ids:
            return self.processed_ids[original]

        # Create a deterministic hash
        hash_obj = hashlib.md5(original.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)
        pseudo_id = f"{prefix}{hash_int % 1000000:06d}"

        self.processed_ids[original] = pseudo_id
        return pseudo_id

    def _generate_pseudo_name(self, original: str, field_type: str = "name") -> str:
        """Generate a pseudo name that indicates the field purpose."""
        if not original or original.strip() == "":
            return "ANONYMOUS"

        if original in self.processed_names:
            return self.processed_names[original]

        # Generate based on hash for consistency
        hash_obj = hashlib.md5(original.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)

        if field_type == "first_name":
            pseudo = f"{self.FIRST_NAMES[hash_int % len(self.FIRST_NAMES)]}{hash_int % 100:02d}"
        elif field_type == "last_name":
            pseudo = f"{self.LAST_NAMES[hash_int % len(self.LAST_NAMES)]}{hash_int % 100:02d}"
        else:
            pseudo = f"Anonymous{hash_int % 1000:03d}"

        self.processed_names[original] = pseudo
        return pseudo

    def _anonymize_date(self, date_str: str) -> str:
        """Anonymize dates by shifting them randomly but consistently."""
        if not date_str or date_str.strip() == "":
            return date_str

        try:
            # Try to parse HL7 datetime format (YYYYMMDD or YYYYMMDDHHmmss)
            if len(date_str) >= 8:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])

                # Keep the year, randomize month and day slightly
                hash_obj = hashlib.md5(date_str.encode())
                hash_int = int(hash_obj.hexdigest()[:8], 16)

                # Shift by consistent amount based on hash
                shift_days = hash_int % 30
                original_date = datetime(year, month, day)
                shifted_date = original_date + timedelta(days=shift_days)

                # Reconstruct in HL7 format
                result = shifted_date.strftime("%Y%m%d")

                # If there was time component, add generic time
                if len(date_str) > 8:
                    result += "120000"  # Noon

                return result
        except (ValueError, IndexError):
            pass

        return date_str

    def _anonymize_address(self, address: str) -> str:
        """Anonymize address information."""
        if not address or address.strip() == "":
            return address

        # Replace with generic address components
        hash_obj = hashlib.md5(address.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)

        return f"Street{hash_int % 100:02d}"

    def _anonymize_phone(self, phone: str) -> str:
        """Anonymize phone numbers."""
        if not phone or phone.strip() == "":
            return phone

        # Keep format but change numbers
        hash_obj = hashlib.md5(phone.encode())
        hash_int = int(hash_obj.hexdigest()[:8], 16)

        return f"+351{hash_int % 1000000000:09d}"

    def anonymize_message(self, message: str) -> str:
        """
        Anonymize an HL7 v2 message in ER7 format.

        Args:
            message: HL7 message string in ER7 format

        Returns:
            Anonymized HL7 message string
        """
        logger.info("Starting message anonymization")

        if not message or message.strip() == "":
            logger.warning("Empty message provided")
            return message

        lines = message.split('\n')
        anonymized_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Split by field separator (|)
            fields = line.split('|')

            if len(fields) == 0:
                anonymized_lines.append(line)
                continue

            segment_type = fields[0]

            # Anonymize based on segment type
            if segment_type == 'PID':
                fields = self._anonymize_pid_segment(fields)
            elif segment_type == 'NK1':
                fields = self._anonymize_nk1_segment(fields)
            elif segment_type == 'PV1':
                fields = self._anonymize_pv1_segment(fields)
            elif segment_type == 'PV2':
                fields = self._anonymize_pv2_segment(fields)
            elif segment_type == 'PD1':
                fields = self._anonymize_pd1_segment(fields)
            elif segment_type == 'OBX':
                fields = self._anonymize_obx_segment(fields)
            elif segment_type == 'ORC' or segment_type == 'OBR':
                fields = self._anonymize_order_segment(fields)
            elif segment_type in ['SCH', 'AIG', 'AIL', 'AIP']:
                fields = self._anonymize_scheduling_segment(fields)
            elif segment_type in ['IN1', 'IN2', 'IN3']:
                fields = self._anonymize_insurance_segment(fields)
            elif segment_type == 'GT1':
                fields = self._anonymize_guarantor_segment(fields)
            elif segment_type == 'ROL':
                fields = self._anonymize_role_segment(fields)
            elif segment_type == 'CTI':
                fields = self._anonymize_cti_segment(fields)
            elif segment_type == 'DG1':
                fields = self._anonymize_dg1_segment(fields)
            elif segment_type == 'PR1':
                fields = self._anonymize_pr1_segment(fields)
            elif segment_type == 'TXA':
                fields = self._anonymize_txa_segment(fields)
            elif segment_type == 'EVN':
                fields = self._anonymize_generic_identifiers(fields)

            anonymized_lines.append('|'.join(fields))

        result = '\n'.join(anonymized_lines)
        logger.info("Message anonymization completed")
        return result

    def _anonymize_pid_segment(self, fields: list) -> list:
        """Anonymize PID (Patient Identification) segment."""
        # PID segment field positions (0-based after split)
        # 0: PID
        # 1: Set ID
        # 2: Patient ID (external) - important
        # 3: Patient ID (internal) - important
        # 4: Alternate Patient ID - important
        # 5: Patient Name - important
        # 6: Mother's Maiden Name
        # 7: Date/Time of Birth
        # 8: Administrative Sex
        # 9: Patient Alias
        # 10: Race
        # 11: Patient Address - important
        # 12: County Code
        # 13: Phone Number - important
        # 14: Business Phone
        # 15: Primary Language
        # 16: Marital Status
        # 17: Religion
        # 18: Patient Account Number - important
        # 19: SSN - important
        # 20: Driver's License Number - important
        # 21: Mother's Identifier
        # 22: Ethnic Group
        # 23: Birth Place
        # 24: Multiple Birth Indicator
        # 25: Birth Order
        # 26: Citizenship
        # 27: Veterans Military Status
        # 28: Nationality
        # 29: Patient Death Date and Time
        # 30: Patient Death Indicator

        if len(fields) > 2:
            # Patient ID (external)
            if fields[2]:
                fields[2] = self._anonymize_composite_id(fields[2])

        if len(fields) > 3:
            # Patient ID (internal)
            fields[3] = self._anonymize_composite_id(fields[3])

        if len(fields) > 4:
            # Alternate Patient ID
            if fields[4]:
                fields[4] = self._anonymize_composite_id(fields[4])

        if len(fields) > 5:
            # Patient Name
            fields[5] = self._anonymize_patient_name(fields[5])

        if len(fields) > 6:
            # Mother's Maiden Name
            if fields[6]:
                fields[6] = self._anonymize_patient_name(fields[6])

        if len(fields) > 7:
            # Date of Birth
            fields[7] = self._anonymize_date(fields[7])

        if len(fields) > 9:
            # Patient Alias
            if fields[9]:
                fields[9] = self._anonymize_patient_name(fields[9])

        if len(fields) > 11:
            # Patient Address
            fields[11] = self._anonymize_composite_address(fields[11])

        if len(fields) > 13:
            # Phone Number
            fields[13] = self._anonymize_phone(fields[13])

        if len(fields) > 14:
            # Business Phone
            fields[14] = self._anonymize_phone(fields[14])

        if len(fields) > 18:
            # Patient Account Number
            fields[18] = self._generate_pseudo_id(fields[18], "ACCT")

        if len(fields) > 19:
            # SSN
            if fields[19]:
                fields[19] = self._generate_pseudo_id(fields[19], "SSN")

        if len(fields) > 20:
            # Driver's License Number
            if fields[20]:
                fields[20] = self._generate_pseudo_id(fields[20], "DL")

        if len(fields) > 21:
            # Mother's Identifier
            if fields[21]:
                fields[21] = self._anonymize_composite_id(fields[21])

        if len(fields) > 23:
            # Birth Place
            if fields[23]:
                fields[23] = "City"

        if len(fields) > 29:
            # Patient Death Date and Time
            if fields[29]:
                fields[29] = self._anonymize_date(fields[29])

        return fields

    def _anonymize_nk1_segment(self, fields: list) -> list:
        """Anonymize NK1 (Next of Kin) segment."""
        # NK1 fields
        # 2: Name
        # 4: Address
        # 5: Phone

        if len(fields) > 2:
            fields[2] = self._anonymize_patient_name(fields[2])

        if len(fields) > 4:
            fields[4] = self._anonymize_composite_address(fields[4])

        if len(fields) > 5:
            fields[5] = self._anonymize_phone(fields[5])

        return fields

    def _anonymize_pv1_segment(self, fields: list) -> list:
        """Anonymize PV1 (Patient Visit) segment."""
        # PV1 fields
        # 7: Attending Doctor
        # 8: Referring Doctor
        # 9: Consulting Doctor
        # 19: Visit Number

        for idx in [7, 8, 9, 17]:
            if len(fields) > idx and fields[idx]:
                fields[idx] = self._anonymize_provider_name(fields[idx])

        if len(fields) > 19:
            fields[19] = self._generate_pseudo_id(fields[19], "VISIT")

        return fields

    def _anonymize_obx_segment(self, fields: list) -> list:
        """Anonymize OBX (Observation) segment - be careful with results."""
        # OBX fields
        # 16: Responsible Observer

        if len(fields) > 16 and fields[16]:
            fields[16] = self._anonymize_provider_name(fields[16])

        return fields

    def _anonymize_order_segment(self, fields: list) -> list:
        """Anonymize ORC/OBR (Order) segments."""
        # Common fields in order segments
        # 2: Placer Order Number
        # 3: Filler Order Number
        # 10: Entered By
        # 12: Ordering Provider

        if len(fields) > 2:
            fields[2] = self._generate_pseudo_id(fields[2], "ORDER")

        if len(fields) > 3:
            fields[3] = self._generate_pseudo_id(fields[3], "ORDER")

        if len(fields) > 10 and fields[10]:
            fields[10] = self._anonymize_provider_name(fields[10])

        if len(fields) > 12 and fields[12]:
            fields[12] = self._anonymize_provider_name(fields[12])

        return fields

    def _anonymize_generic_identifiers(self, fields: list) -> list:
        """Anonymize generic user/operator fields."""
        # Look for common operator/user fields
        for i in range(len(fields)):
            field = fields[i]
            # Check if field looks like a user ID or operator
            if field and ('^' in field or field.isupper()):
                if '^' in field:
                    fields[i] = self._anonymize_provider_name(field)

        return fields

    def _anonymize_composite_id(self, composite: str) -> str:
        """Anonymize composite ID field (with ^ separators)."""
        if not composite or composite.strip() == "":
            return composite

        parts = composite.split('^')
        if len(parts) > 0 and parts[0]:
            parts[0] = self._generate_pseudo_id(parts[0], "PID")

        return '^'.join(parts)

    def _anonymize_patient_name(self, name: str) -> str:
        """Anonymize patient name (last^first^middle format)."""
        if not name or name.strip() == "":
            return name

        parts = name.split('^')

        if len(parts) > 0 and parts[0]:
            parts[0] = self._generate_pseudo_name(parts[0], "last_name")

        if len(parts) > 1 and parts[1]:
            parts[1] = self._generate_pseudo_name(parts[1], "first_name")

        if len(parts) > 2 and parts[2]:
            parts[2] = self._generate_pseudo_name(parts[2], "first_name")

        return '^'.join(parts)

    def _anonymize_provider_name(self, name: str) -> str:
        """Anonymize provider/doctor name."""
        if not name or name.strip() == "":
            return name

        parts = name.split('^')

        if len(parts) > 0 and parts[0]:
            parts[0] = f"Dr{self._generate_pseudo_name(parts[0], 'last_name')}"

        if len(parts) > 1 and parts[1]:
            parts[1] = self._generate_pseudo_name(parts[1], "first_name")

        return '^'.join(parts)

    def _anonymize_composite_address(self, address: str) -> str:
        """Anonymize composite address field (with ^ separators)."""
        if not address or address.strip() == "":
            return address

        parts = address.split('^')

        # Anonymize street address
        if len(parts) > 0 and parts[0]:
            parts[0] = self._anonymize_address(parts[0])

        # Keep city/state/zip structure but anonymize
        if len(parts) > 1 and parts[1]:
            parts[1] = "City"

        if len(parts) > 3 and parts[3]:
            parts[3] = "12345"

        return '^'.join(parts)

    def _anonymize_scheduling_segment(self, fields: list) -> list:
        """Anonymize SCH/AIG/AIL/AIP (Scheduling) segments."""
        # These segments contain provider names and identifiers
        # SCH: fields 15-16 contain provider info
        # AIG: field 3 contains resource ID (provider)
        # AIL: field 3 contains location
        # AIP: field 3 contains provider info

        segment_type = fields[0] if len(fields) > 0 else ""

        if segment_type == 'SCH':
            # Fields 15 and 16 may contain provider names
            if len(fields) > 15 and fields[15] and '^' in fields[15]:
                fields[15] = self._anonymize_provider_name(fields[15])
            if len(fields) > 16 and fields[16] and '^' in fields[16]:
                fields[16] = self._anonymize_provider_name(fields[16])

        elif segment_type == 'AIG':
            # Field 3 contains resource ID (provider identifier/name)
            if len(fields) > 3 and fields[3] and '^' in fields[3]:
                fields[3] = self._anonymize_provider_name(fields[3])

        elif segment_type == 'AIP':
            # Field 3 contains provider information
            if len(fields) > 3 and fields[3] and '^' in fields[3]:
                fields[3] = self._anonymize_provider_name(fields[3])
            # Field 5 may also contain provider info
            if len(fields) > 5 and fields[5] and '^' in fields[5]:
                fields[5] = self._anonymize_provider_name(fields[5])

        return fields

    def _anonymize_pv2_segment(self, fields: list) -> list:
        """Anonymize PV2 (Patient Visit - Additional Info) segment."""
        # PV2 fields with PHI
        # 13: Referral Source Name
        # 23: Clinic Organization Name

        if len(fields) > 13 and fields[13]:
            if '^' in fields[13]:
                fields[13] = self._anonymize_provider_name(fields[13])

        if len(fields) > 23 and fields[23]:
            fields[23] = "Medical Center"

        return fields

    def _anonymize_pd1_segment(self, fields: list) -> list:
        """Anonymize PD1 (Patient Demographics) segment."""
        # PD1 fields with PHI
        # 4: Primary Care Provider Name and ID
        # 14: Place of Worship
        # 15: Advance Directive Code

        if len(fields) > 4 and fields[4]:
            if '^' in fields[4]:
                fields[4] = self._anonymize_provider_name(fields[4])

        if len(fields) > 14 and fields[14]:
            fields[14] = ""

        return fields

    def _anonymize_insurance_segment(self, fields: list) -> list:
        """Anonymize IN1/IN2/IN3 (Insurance) segments."""
        segment_type = fields[0] if len(fields) > 0 else ""

        if segment_type == 'IN1':
            # IN1 - Insurance primary info
            # 3: Insurance Company ID
            # 4: Insurance Company Name
            # 5: Insurance Company Address
            # 6: Insurance Company Contact Person
            # 7: Insurance Company Phone
            # 16: Name of Insured
            # 17: Insured's Relationship to Patient
            # 19: Insured's Address
            # 20: Assignment of Benefits
            # 36: Policy Number
            # 49: Insured's ID Number

            if len(fields) > 3 and fields[3]:
                fields[3] = self._generate_pseudo_id(fields[3], "INS")

            if len(fields) > 4 and fields[4]:
                fields[4] = "Insurance Company"

            if len(fields) > 5 and fields[5]:
                fields[5] = self._anonymize_composite_address(fields[5])

            if len(fields) > 6 and fields[6]:
                if '^' in fields[6]:
                    fields[6] = self._anonymize_patient_name(fields[6])

            if len(fields) > 7 and fields[7]:
                fields[7] = self._anonymize_phone(fields[7])

            if len(fields) > 16 and fields[16]:
                if '^' in fields[16]:
                    fields[16] = self._anonymize_patient_name(fields[16])

            if len(fields) > 19 and fields[19]:
                fields[19] = self._anonymize_composite_address(fields[19])

            if len(fields) > 36 and fields[36]:
                fields[36] = self._generate_pseudo_id(fields[36], "POL")

            if len(fields) > 49 and fields[49]:
                fields[49] = self._generate_pseudo_id(fields[49], "INSID")

        elif segment_type == 'IN2':
            # IN2 - Insurance additional info
            # 1: Insured's Employee ID
            # 2: Insured's SSN
            # 6: Medicare Health Insurance Card Number
            # 26: Payor Subscriber ID
            # 61: Insured's Phone Number
            # 63: Insured's Employer's Address
            # 72: Insured's Employer Name

            if len(fields) > 1 and fields[1]:
                fields[1] = self._generate_pseudo_id(fields[1], "EMP")

            if len(fields) > 2 and fields[2]:
                fields[2] = self._generate_pseudo_id(fields[2], "SSN")

            if len(fields) > 6 and fields[6]:
                fields[6] = self._generate_pseudo_id(fields[6], "MED")

            if len(fields) > 26 and fields[26]:
                fields[26] = self._generate_pseudo_id(fields[26], "SUB")

            if len(fields) > 61 and fields[61]:
                fields[61] = self._anonymize_phone(fields[61])

            if len(fields) > 63 and fields[63]:
                fields[63] = self._anonymize_composite_address(fields[63])

            if len(fields) > 72 and fields[72]:
                fields[72] = "Company Name"

        return fields

    def _anonymize_guarantor_segment(self, fields: list) -> list:
        """Anonymize GT1 (Guarantor) segment."""
        # GT1 fields with PHI
        # 2: Guarantor Number
        # 3: Guarantor Name
        # 5: Guarantor Address
        # 6: Guarantor Phone
        # 7: Guarantor Business Phone
        # 10: Guarantor Type
        # 12: Guarantor SSN
        # 15: Guarantor Employer Name
        # 16: Guarantor Employer Address
        # 17: Guarantor Employer Phone

        if len(fields) > 2 and fields[2]:
            fields[2] = self._generate_pseudo_id(fields[2], "GUAR")

        if len(fields) > 3 and fields[3]:
            if '^' in fields[3]:
                fields[3] = self._anonymize_patient_name(fields[3])

        if len(fields) > 5 and fields[5]:
            fields[5] = self._anonymize_composite_address(fields[5])

        if len(fields) > 6 and fields[6]:
            fields[6] = self._anonymize_phone(fields[6])

        if len(fields) > 7 and fields[7]:
            fields[7] = self._anonymize_phone(fields[7])

        if len(fields) > 12 and fields[12]:
            fields[12] = self._generate_pseudo_id(fields[12], "SSN")

        if len(fields) > 15 and fields[15]:
            fields[15] = "Employer Name"

        if len(fields) > 16 and fields[16]:
            fields[16] = self._anonymize_composite_address(fields[16])

        if len(fields) > 17 and fields[17]:
            fields[17] = self._anonymize_phone(fields[17])

        return fields

    def _anonymize_role_segment(self, fields: list) -> list:
        """Anonymize ROL (Role) segment."""
        # ROL fields with PHI
        # 4: Role Person - provider/person name

        if len(fields) > 4 and fields[4]:
            if '^' in fields[4]:
                fields[4] = self._anonymize_provider_name(fields[4])

        return fields

    def _anonymize_cti_segment(self, fields: list) -> list:
        """Anonymize CTI (Clinical Trial Identification) segment."""
        # CTI fields with PHI
        # 3: Study Participating Person

        if len(fields) > 3 and fields[3]:
            if '^' in fields[3]:
                fields[3] = self._anonymize_provider_name(fields[3])

        return fields

    def _anonymize_dg1_segment(self, fields: list) -> list:
        """Anonymize DG1 (Diagnosis) segment."""
        # DG1 fields with PHI
        # 16: Diagnosing Clinician

        if len(fields) > 16 and fields[16]:
            if '^' in fields[16]:
                fields[16] = self._anonymize_provider_name(fields[16])

        return fields

    def _anonymize_pr1_segment(self, fields: list) -> list:
        """Anonymize PR1 (Procedures) segment."""
        # PR1 fields with PHI
        # 11: Surgeon
        # 12: Procedure Practitioner

        if len(fields) > 11 and fields[11]:
            if '^' in fields[11]:
                fields[11] = self._anonymize_provider_name(fields[11])

        if len(fields) > 12 and fields[12]:
            if '^' in fields[12]:
                fields[12] = self._anonymize_provider_name(fields[12])

        return fields

    def _anonymize_txa_segment(self, fields: list) -> list:
        """Anonymize TXA (Transcription Document Header) segment."""
        # TXA fields with PHI
        # 5: Activity Date/Time
        # 9: Originator Code/Name - provider who created the document
        # 10: Assigned Document Authenticator - provider who authenticated
        # 11: Transcriptionist Code/Name
        # 22: Authentication Person, Time Stamp

        if len(fields) > 5 and fields[5]:
            # Activity Date/Time
            fields[5] = self._anonymize_date(fields[5])

        if len(fields) > 9 and fields[9]:
            # Originator Code/Name (provider)
            if '^' in fields[9]:
                fields[9] = self._anonymize_provider_name(fields[9])

        if len(fields) > 10 and fields[10]:
            # Assigned Document Authenticator (provider)
            if '^' in fields[10]:
                fields[10] = self._anonymize_provider_name(fields[10])

        if len(fields) > 11 and fields[11]:
            # Transcriptionist Code/Name
            if '^' in fields[11]:
                fields[11] = self._anonymize_provider_name(fields[11])

        if len(fields) > 22 and fields[22]:
            # Authentication Person, Time Stamp
            if '^' in fields[22]:
                # This field contains both person and timestamp, anonymize the person part
                fields[22] = self._anonymize_provider_name(fields[22])

        return fields
