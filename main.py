from dotenv import load_dotenv
import requests
import time
import os
import smtplib
from lxml import html

load_dotenv()

EMAIL1 = os.getenv("EMAIL1")
EMAIL2 = os.getenv("EMAIL2")
PASSWORD = os.getenv("PASSWORD")
MY_EMAIL_GOOGLE = os.getenv("MY_EMAIL_GOOGLE")
PASSWORD_GOOGLE = os.getenv("PASSWORD_GOOGLE")

LOGIN_URL = "https://myupway.com/LogIn"
SERVICE_INFO0 = "https://myupway.com/System/168599/Status/ServiceInfo/0"
SERVICE_INFO1 = "https://myupway.com/System/168599/Status/ServiceInfo/1"

session_requests = requests.session()

payload = {
    "Email": EMAIL1,
    "Password": PASSWORD,
}

session_requests.get(LOGIN_URL)
session_requests.post(
    LOGIN_URL,
    data=payload,
)


def send_email(email1=None, email2=None, message=None):
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL_GOOGLE, password=PASSWORD_GOOGLE)
        connection.sendmail(
            from_addr=MY_EMAIL_GOOGLE,
            to_addrs=[email1, email2],
            msg=message
        )


def getting_data():
    global same_time
    same_time = None
    is_running = True
    while is_running:
        result_info0 = session_requests.get(SERVICE_INFO0, headers=dict(referer=SERVICE_INFO0))
        tree_info0 = html.fromstring(result_info0.content)
        temp_outside = tree_info0.xpath('//*[@id="EmilContentColumn"]/table[1]/tbody/tr[4]/td[2]/span')[
            0].text_content()
        current_driver = tree_info0.xpath('//*[@id="EmilContentColumn"]/table[1]/tbody/tr[6]/td[2]/span')[
            0].text_content()
        current_heat_pomp = tree_info0.xpath('//*[@id="EmilContentColumn"]/table[1]/tbody/tr[7]/td[2]/span')[
            0].text_content()
        event = tree_info0.xpath('//*[@id="EmilContentColumn"]/div[1]/div[2]')[0].text_content()
        hot_water_temp = tree_info0.xpath('//*[@id="EmilContentColumn"]/table[1]/tbody/tr[3]/td[2]/span')[
            0].text_content()
        try:
            time_received = tree_info0.xpath('//*[@id="EmilContentColumn"]/div[1]/div[3]')[0].text_content()
        except IndexError:
            time_received = None
        # time_received = "10"

        result_info1 = session_requests.get(SERVICE_INFO1, headers=dict(referer=SERVICE_INFO1))
        tree_info1 = html.fromstring(result_info1.content)
        defrosting = tree_info1.xpath('//*[@id="EmilContentColumn"]/table[1]/tbody/tr[1]/td[2]/span')[
            0].text_content().title()
        blocked = tree_info1.xpath('//*[@id="EmilContentColumn"]/table[2]/tbody/tr[1]/td[2]/span')[
            0].text_content().title()
        charge_pump_speed = tree_info1.xpath('//*[@id="EmilContentColumn"]/table[1]/tbody/tr[2]/td[2]/span')[
            0].text_content()

        print(f"Defrosting: {defrosting}")
        print(f"Blocked: {blocked}")
        print(f"Outdoor temperature: {temp_outside}")
        print(f"Current heat pomp: {current_heat_pomp}")
        print(f"Charge pump speed: {charge_pump_speed}")
        print(f"Current driver: {current_driver}")
        print(f"Hot water temperature: {hot_water_temp}")
        print("------------")

        if same_time != time_received:
            # if True:
            if event == "Defrosting in progress " or event == "Compressor limited by load monitor":
                same_time = time_received
                message = f"Subject:New event detected in system\n\nSystem status information:\n\n" \
                          f"{event}\n{time_received}\n\n" \
                          f"Basic parameters:\n\n" \
                          f"Defrosting: {defrosting}\n" \
                          f"Blocked: {blocked}\n" \
                          f"Outdoor temperature: {temp_outside}\n" \
                          f"Current heat pomp: {current_heat_pomp}\n" \
                          f"Charge pump speed: {charge_pump_speed}\n" \
                          f"Current driver: {current_driver}\n" \
                          f"Hot water temperature: {hot_water_temp}"
                send_email(email1=EMAIL1, email2=EMAIL1, message=message)
                print("Mails sent\n")

        time.sleep(60)


def app():
    getting_data()


if __name__ == "__main__":
    app()
