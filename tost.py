from yandex_money import api

print(api.Wallet.build_obtain_token_url(client_id='103703A821D04244A16FA4554553725282C76EF2E5491E3690FAC425D7665EB4',redirect_uri='https://104.155.124.29:8443/ya_pay',scope=['account-info', 'operation-history','operation-details'])+'&response_type=code')

# Empty webserver index, return nothing, just http 200


wallet = api.Wallet(access_token='410011460693944.8EA33E1F4681E30270A8FF1668BEA0025CC75F5FFA72100BC082F0FE5319F9E06EB4696A4C874D4C07233D557EED7B08033597302898119624A433FF2BE4925D2C0E176AB06BE1DDE2B97EB6DB9258222C032C7CC3741F5ABF91A7B24AC8839B832FD968C1B76CBCCDA7849904B01602F3786253C1923D2903C18A4A124C487E')
print(wallet.operation_details(operation_id=512742676385025004))
print(wallet.operation_history({'type':'deposition','details':'true'}))

# app.run(host=settings.WEBHOOK_LISTEN,
#         port=settings.WEBHOOK_PORT,
#         ssl_context=(settings.WEBHOOK_SSL_CERT, settings.WEBHOOK_SSL_PRIV),debug=False)