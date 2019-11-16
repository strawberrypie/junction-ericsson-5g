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
	        withCredentials([string(credentialsId: 'hub.docker.com', variable: 'PASSWORD')]) {
		    sh "docker login -u=dfkozlov -p=$PASSWORD"
		    sh "make push"
		}
            }
        }
    }
}
