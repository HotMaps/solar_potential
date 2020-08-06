node {
  stage('Init') {
    checkout scm
    sh 'cp /home/jenkins/hotmaps/cm/.env ./cm/.env'
  }

  stage('Build & Test') {
    try {
      sh 'docker-compose -f docker-compose.tests.yml build --no-cache && docker-compose -f docker-compose.tests.yml -p hotmaps up --force-recreate --exit-code-from solar_potential'
    }
    finally {
      // stop services
      sh 'docker-compose -f docker-compose.tests.yml down'
    }
  }
}
