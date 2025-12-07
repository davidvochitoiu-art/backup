class SecurityIncident:
    """Represents a cybersecurity incident."""

    def __init__(self, incident_id, incident_type, severity, status, description):
        self.__id = incident_id
        self.__incident_type = incident_type
        self.__severity = severity
        self.__status = status
        self.__description = description

    def get_id(self):
        return self.__id

    def get_incident_type(self):
        return self.__incident_type

    def get_severity(self):
        return self.__severity

    def get_status(self):
        return self.__status

    def get_description(self):
        return self.__description

    def update_status(self, new_status):
        self.__status = new_status

    def get_severity_level(self):
        mapping = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return mapping.get(self.__severity.lower(), 0)
