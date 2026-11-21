from database import engine
#库地址、账号密码、用哪个驱动，全在它身上。这一行等于说 “我知道怎么连库了”。

from models import Base#把表定义装进册子


Base.metadata.create_all(engine)