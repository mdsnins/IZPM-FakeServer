SQLITE_DB = "sqlite://izpm.db"

SERVER_NAME = "izone-mail.com"

API_SUBDOMAIN = "app-api"
WEB_SUBDOMAIN = "app-web"
IMG_SUBDOMAIN = "app-img"

API_HOST   = "http://{}.{}".format(API_SUBDOMAIN, SERVER_NAME)
WEB_HOST   = "http://{}.{}".format(WEB_SUBDOMAIN, SERVER_NAME)
IMG_HOST   = "http://{}.{}".format(IMG_SUBDOMAIN, SERVER_NAME)

IMAGE_PREFIX  = IMG_HOST + "/artist/profile/starship/202010211113"
DETAIL_PREFIX = WEB_HOST + "/mail"

