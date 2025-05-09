import time
import subprocess
import ipperfGetBandWidth
import getPjsipEndpoints
import pjsip_manager

from ipperfGetBandWidth import get_iperf_bandwidth
from getPjsipEndpoints import get_active_pjsip_endpoint_details
from pjsip_manager import  PJSIPManager

def optimize():

    endpoints=get_active_pjsip_endpoint_details()
    manager=PJSIPManager()
    infoUsers=[]

    for endpoint in endpoints:

        bd=get_iperf_bandwidth(server_ip=endpoint['ip'],duration=3)
            
        infoUsers.append({
                'id':endpoint['numero'],
                'ip':endpoint['ip'],
                'bandWidth':bd
            })
        
    for user in infoUsers:
        if user['bandWidth']:
            if user['bandWidth'] > 0.064:
                manager.edit_user(extension=user['id'],codecs='ulaw,alaw,opus,g729,gsm')
            elif user['bandWidth'] > 0.008:
                manager.edit_user(extension=user['id'],codecs='g729,opus,ulaw,alaw,gsm')
            else:
                manager.edit_user(extension=user['id'],codecs='opus,gsm,ulaw,alaw,g729')
            manager.show_user(extension=user['id'])
    return endpoints

if __name__ == "__main__":

    command = ['./asteriskReload.sh']
    while True:
        endp=optimize()
        print(f"exécution de l'optimizer toutes les {5 * 60 * len(endp)} secondes")
        subprocess.run(command, capture_output=True, text=True, check=True)
       # time.sleep(5*len(endp))
        time.sleep(5*60*len(endp))

         
