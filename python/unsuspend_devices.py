from libs.functions import okta_api_call, get_okta_token_read_only, get_local_okta_admin_token

domain = "example"
base_url = f"https://{domain}.okta.com/api/v1"
scopes = "okta.devices.read"

"""
lists out all suspended desktop computers in okta
will reactivate them all
designed to quickly activate everything suspended

this is in case troubleshooting around why so many are suspended
becomes too arduous and we wanna get all active and then suspend back the ones we dont want
---
mostly adapted out of get_devices.py
---
tokens:
set to use a local admin token for the changes
but can read with an API service app
"""


def list_suspended_devices(token):
    """
    searchs Okta for suspended MACOS and WINDOWS
    """
    device_url = f"{base_url}/devices"
    # define platforms as an array, we can't filter for both at once
    platforms = ["MACOS", "WINDOWS"]
    # create devices list to fill to
    devices = []

    # list out all the suspended for both the macos and windows
    for platform in platforms:
        query = {
            "limit": "50",
            "expand": "user",
            "filter": f'status eq "SUSPENDED" and profile.platform eq "{platform}"'
        }

        result = okta_api_call(
            url=device_url,
            token=token,
            method='get',
            body=None,
            query=query
        )
        devices.extend(result)  # add to the devices list

    return devices


def unsuspend_devices(devices, token):
    """
    activates all the devices from the suspended device list
    """
    for device in devices:
        # get the id and platform
        device_id = device.get("id")
        platform = device["profile"].get("platform", "")
        # print on screen for un-suspended 
        print(f"Activating device {device_id} ({platform})")
        # ^^ this might be too noisy

        """
        activate the device with the ID
        https://developer.okta.com/docs/api/openapi/okta-management/management/tag/Device/#tag/Device/operation/activateDevice
        """
        activate_url = f"{base_url}/devices/{device_id}/lifecycle/activate"
        try:
            okta_api_call(
                url=activate_url,
                token=token,
                method="post"
            )
            print(f"Activated {device_id}")
        except Exception as error:
            print(f"Failure for {device_id}.\n {error}")


def main():
    bearer_token = get_okta_token_read_only(scopes)
    token = f"Bearer {bearer_token}"

    suspended_devices = list_suspended_devices(token)
    # print out how many suspended devices were found
    print(f"Found {len(suspended_devices)} suspended dekstop devices")

    if suspended_devices:
        # get the local admin token so we can actually execute changes
        write_token = get_local_okta_admin_token()
        unsuspend_devices(suspended_devices, write_token)


if __name__ == "__main__":
    main()