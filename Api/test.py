from easywebdav import Client


client = Client("pan.xingyv.site", port=443, username='weiwei', password='gsw091005', path='dav', protocol='https')

client.ls("/")
