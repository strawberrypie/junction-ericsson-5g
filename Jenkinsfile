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
                docker.withRegistry('https://registry.hub.docker.com', 'hub.docker.com') {
                    sh "make push"
		}
            }
        }
    }
}
