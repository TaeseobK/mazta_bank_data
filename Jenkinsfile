pipeline {
  agent any
  stages {
    stage('Pull Latest Code') {
      steps {
        sh '''
          mkdir -p ~/.ssh
          chmod 0700 ~/.ssh
          ssh-keyscan 172.17.0.1 >> ~/.ssh/known_hosts
          chmod 644 ~/.ssh/known_hosts
          ssh mazta@172.17.0.1 "cd /home/mazta/product_pusatdata && git pull origin main"
        '''
      }
    }
  }
}
