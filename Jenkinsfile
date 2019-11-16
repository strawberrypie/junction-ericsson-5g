pipeline {
    agent {
        label "jenkins-cpu"
    }
    stages {
        stage("Build") {
            steps {
                cleanWs()
                checkout scm
                sh "make build"
            }
        }
        stage("Push") {
            steps {
                sh "make push"
            }
        }
    }
    post {
        always {
                cleanWs()
        }
    }
}
