# root path:
name = 'test'
path_root = ''

# folder path:
file_folder = '{}/{}/desc'.format(path_root, name)
image_folder = '{}/{}/img'.format(path_root, name)
screenshot_folder = '{}/{}/screenshot'.format(path_root, name)

# file path
meta_path = '{}/meta.json'.format(file_folder)
src_path = '{}/src.json'.format(file_folder)
image_path = '{}/paths.json'.format(file_folder)
tag_path = '{}/tag.json'.format(file_folder)

cookie = ''
referer = ''

default_headers = ''

# category
classid = 6
source_name = "toutiao"

# database
# MongoDB
db_settings = {
    "MONGODB_SERVER": "127.0.0.1",
    "MONGODB_PORT": 27017,
    "MONGODB_DB": "",
    "MONGODB_META_COLLECTION": "metadata",
    "MONGODB_SOURCE_COLLECTION": "sourcedata",
    "MONGODB_PATH_COLLECTION": "pathdata",
    "MONGODB_TAGS_COLLECTION": "tagsdata"
}