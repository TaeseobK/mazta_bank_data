pipeline {
  agent any
  stages {
    stage('Pull Latest Code') {
      steps {
        sh '''
        ssh mazta@172.17.0.1 "cd /home/mazta/product_pusatdata && git pull origin main"
        '''
      }
    }
  }
}
