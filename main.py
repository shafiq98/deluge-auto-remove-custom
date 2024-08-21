# This is a test python file to mess around with other things
# from dotenv import load_dotenv
import logging
import os

# load_dotenv()  # take environment variables from .env.
log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

if __name__ == "__main__":
    target_path = "./"
    file_list = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]

    for file in file_list:
        file_path: str = os.path.join("./", file)
        file_has_hardlink = True if os.stat(file_path).st_nlink > 1 else False
        if not file_has_hardlink:
            # TODO: Run deluge delete logic here
            log.info(file)