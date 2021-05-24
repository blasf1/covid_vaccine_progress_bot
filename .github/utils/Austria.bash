#!/bin/bash
cat <<EOF > ssl_conf
openssl_conf = default_conf

[ default_conf ]

ssl_conf = ssl_sect

[ssl_sect]

system_default = system_default_sect

[system_default_sect]
MinProtocol = TLSv1.2
CipherString = DEFAULT:@SECLEVEL=1
EOF

export OPENSSL_CONF="$(pwd)/ssl_conf"
