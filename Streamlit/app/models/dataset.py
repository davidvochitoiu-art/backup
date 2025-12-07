class Dataset:
    """Represents a dataset entry from datasets_metadata table."""

    def __init__(self, dataset_id, name, rows, columns, uploaded_by, upload_date):
        self.__id = dataset_id
        self.__name = name
        self.__rows = rows
        self.__columns = columns
        self.__uploaded_by = uploaded_by
        self.__upload_date = upload_date

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_rows(self):
        return self.__rows

    def get_columns(self):
        return self.__columns

    def get_uploaded_by(self):
        return self.__uploaded_by

    def get_upload_date(self):
        return self.__upload_date

    def calculate_size_mb(self):
        """Estimate dataset size based on rows × columns × 8 bytes."""
        if self.__rows is None or self.__columns is None:
            return 0.0
        size_bytes = self.__rows * self.__columns * 8
        return round(size_bytes / (1024 * 1024), 2)
