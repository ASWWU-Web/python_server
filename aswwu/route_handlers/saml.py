import logging

from aswwu import BaseHandler
from settings import keys

logger = logging.getLogger("aswwu")

class SamlHandler(BaseHandler):
    def post(self):
        try:
            secret_key = self.get_argument('secret_key', None)
            if(secret_key == keys["samlEndpointKey"]):
                employee_id = self.get_argument('employee_id', None)
                full_name = self.get_argument('full_name', None)
                email_address = self.get_argument('email_address', None)
                if employee_id:
                    user = query_user(employee_id)
                    if not user:
                        user = User(wwuid=employee_id, username=email_address.split('@',1)[0], full_name=full_name, status='Student')
                        addOrUpdate(user)
                    self.write({'status':'success'})
                else:
                    logger.info("AccountHandler: error")
                    self.write({'error':'invalid parameters'})
            else:
                logger.info("Unauthorized Access Attempted")
                self.write({'error':'Unauthorized Access Attempted'})
        except Exception as e:
            logger.error("LoginHandler: error"+str(e.message))
            self.write({'error': str(e.message)})
    def get(self):
        self.write({'error':'You really should not be here'})
