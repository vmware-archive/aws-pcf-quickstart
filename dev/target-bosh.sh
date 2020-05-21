export OM_TARGET=$1
export OM_USERNAME=admin
export OM_PASSWORD=$2
export OM_SKIP_SSL_VALIDATION=true
export SSH_KEY_PATH=$3

while read var; do unset $var; done < <(env | grep BOSH | cut -d'=' -f1)

export BOSH_ALL_PROXY="ssh+socks5://ubuntu@${OM_TARGET}:22?private-key=${SSH_KEY_PATH}"
BOSH_PRODUCT_GUID=$(om curl -s -path /api/v0/deployed/products/ | jq -r -c '.[] | select(.type | contains("p-bosh")) | .guid');
export BOSH_ENVIRONMENT=$(om curl -s -path /api/v0/deployed/products/$BOSH_PRODUCT_GUID/static_ips | jq -r '.[].ips[]');
export BOSH_CA_CERT=$(om curl -s -path /api/v0/certificate_authorities | jq -r '.certificate_authorities[].cert_pem');
export BOSH_USERNAME=$(om curl -s -path /api/v0/deployed/director/credentials/director_credentials | jq -r '.credential.value.identity');
export BOSH_PASSWORD=$(om curl -s -path /api/v0/deployed/director/credentials/director_credentials | jq -r '.credential.value.password');
echo -e "$BOSH_USERNAME\n$BOSH_PASSWORD\n" | bosh log-in