node {
  stage('Init') {
    checkout scm
  }
    
  stage('Build & Test') {
    try {
      sh 'docker-compose -f docker-compose-tests.yml up --build'
    }
    finally {
      // stop services
      sh 'docker-compose -f docker-compose-tests.yml down' 
    }
  }
  
  // get commit id
  env.COMMIT_ID = sh(returnStdout: true, script: 'git rev-parse HEAD')
  
  stage('Deploy') {
    if (env.BRANCH_NAME == 'develop') {
      echo "Deploying to DEV platform"
      //commitId = sh(returnStdout: true, script: 'git rev-parse HEAD')
      echo "Deploying commit \$COMMIT_ID"
      //sshagent(['sshhotmapsdev']) {
      //  sh 'ssh -o StrictHostKeyChecking=no -l iig hotmapsdev.hevs.ch "/var/hotmaps/deploy_backend.sh \$COMMIT_ID"'
      //}
    } else if (env.BRANCH_NAME == 'master') {
      echo "Deploying to PROD platform"
      echo "Deployment to PROD is currently disabled"
    } else {
      echo "${env.BRANCH_NAME}: not deploying"
    }
  }
}
