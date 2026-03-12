import gspread


def get_client(credentials_path: str) -> gspread.Client:
    return gspread.service_account(filename=credentials_path)
