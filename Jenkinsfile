pipeline {
  agent any
  stages {
    stage('Pull Latest Code') {
      steps {
        sshagent(['ssh-mazta']) {
          sh '''
            ssh -o StrictHostKeyChecking=no mazta@172.17.0.1 "cd /home/mazta/product_pusatdata && git pull origin main"
          '''
        }
      }
    }
  }
}

