fullzip:
	# pip install --target ./package mypackage to add more
	cd package && zip -r9 ${OLDPWD}/function.zip .
	zip -g function.zip function.py

zip:
	zip -g function.zip function.py

upload: zip
	aws --region us-west-2 lambda update-function-code --function-name biothings-farm-cognito-checker --zip-file fileb://function.zip
