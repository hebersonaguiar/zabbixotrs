node('master') {
    stage('Git Pull Script') {
        git branch: 'master',
        credentialsId: '3fb868ca-b81c-4f9d-b7a2-11016ad9e6b0',
        url: 'https://github.com/hebersonaguiar/zabbixotrs.git'
    }

    stage('Exec Script')
        withCredentials([
            usernamePassword(credentialsId: 'aa878f4c-102b-49c0-93c5-72c35acdf30a', usernameVariable: 'ZABBIXU', passwordVariable: 'ZABBIXP'),
            usernamePassword(credentialsId: '04fef6d6-a5a5-4e2c-86c9-f5e313514910', usernameVariable: 'OTRSU', passwordVariable: 'OTRSP'),
            usernamePassword(credentialsId: 'c670cadc-d2f7-4e1e-a54d-4520d4141792', usernameVariable: 'OTRSDBU', passwordVariable: 'OTRSDBP')
        ]){
            sh "/usr/bin/python zabbixotrs.py $ZABBIXU $ZABBIXP $OTRSU $OTRSP $OTRSDBU '$OTRSDBP'"
    }
}
