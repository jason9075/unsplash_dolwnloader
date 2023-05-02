import dotenv
import requests
import os
import concurrent.futures
from tqdm import tqdm

dotenv.load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
UNSPLASH_USER = "andrewnef"

DOMAIN = "https://api.unsplash.com"
API_GET_PUBLIC_PROFILE = f"{DOMAIN}/users/{UNSPLASH_USER}?client_id={ACCESS_KEY}"
API_GET_LIST_PHOTOS = f"{DOMAIN}/users/{UNSPLASH_USER}/photos?client_id={ACCESS_KEY}"


def main():
    # Get a user’s public profile
    # https://unsplash.com/documentation#get-a-users-public-profile
    # GET /users/:username
    response = requests.get(API_GET_PUBLIC_PROFILE)

    data = response.json()
    # get total photos of user
    total_photos = data["total_photos"]
    print(f"Total photos: {total_photos}")

    # Get a list of photos uploaded by a user.
    # https://unsplash.com/documentation#get-a-list-of-photos-uploaded-by-a-user
    # GET /users/:username/photos

    # download list of photos to downloaded folder
    idx = 0
    page = 1

    # use multi thread to download, limit 10 threads
    with tqdm(total=total_photos) as pbar:
        while idx < total_photos:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                response = requests.get(f"{API_GET_LIST_PHOTOS}&page={page}")
                data = response.json()
                download_list_photo(executor, data)
                # wait complete batch download
                executor.shutdown(wait=True)
                idx += len(data)
                pbar.update(len(data))
                page += 1


def download_list_photo(executor, data):
    for photo in data:
        url = photo["urls"]["raw"]
        filename = f"downloaded/{photo['id']}.jpg"
        # check exist file
        if os.path.exists(filename):
            return
        executor.submit(download_photo, url, filename)


def download_photo(url, filename):
    response = requests.get(url)
    with open(filename, "wb") as file:
        file.write(response.content)


if __name__ == "__main__":
    main()
