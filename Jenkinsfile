stages {
    stage('Pull Latest Code') {
        steps {
            sh '''
            ssh mazta@localhost "cd /home/mazta/product_pusatdata && git pull origin main"
            git pull origin main
            '''
        }
    }
}