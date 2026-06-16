import json, urllib.request, urllib.parse, time

k=open(".agnes_key").read().strip()
base="https://apihub.agnes-ai.com/v1"
headers={"Authorization":"Bearer "+k,"Content-Type":"application/json"}

# Step 1: Generate character sheet for 萧炎
prompt="""anime manga style character reference sheet, full body front view, 
young male age 15, handsome, black hair flowing, black eyes determined expression, 
gray martial arts robes, ancient Chinese wuxia setting, 
clean vibrant illustration, highly detailed face and costume, white background"""

data=json.dumps({"model":"agnes-image-2.1-flash","prompt":prompt,"size":"1024x1024"}).encode()
req=urllib.request.Request(base+"/images/generations",headers=headers,data=data)
resp=urllib.request.urlopen(req,timeout=120)
result=json.loads(resp.read().decode())
url=result.get("data",[{}])[0].get("url","")
print("Character sheet: %s" % (url[:80] if url else "FAILED"))
