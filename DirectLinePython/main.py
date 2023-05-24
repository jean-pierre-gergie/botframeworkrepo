from helpers.direct_line_api_helper import DirectLineAPI

from time import sleep


def main():

    api=DirectLineAPI("kvuL934pimQ.2WLqGz5dnuyeOU3m_OGoZjU51__mJCT_Ak06jhWJKpw")


    api.set_headers()

    sleep(2)


    sleep(2)
    api.start_conversation()

    sleep(2)
    response = api.send_message("jpseph kifak")
    print(response)
    sleep(2)
    sleep(2)
    sleep(2)
    sleep(2)
    sleep(2)

    response1 = api.get_message()
    print("waiting")
    sleep(2)
    sleep(2)
    sleep(2)
    sleep(2)

    print(response1+"here we wait for the response")


if __name__ == "__main__":

    main()