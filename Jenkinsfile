pipeline {
    agent {
        label "jenkins-cpu"
    }
    stages {
        stage("Build") {
            steps {
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
}
