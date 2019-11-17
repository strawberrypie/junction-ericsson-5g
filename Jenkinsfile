pipeline {
    agent {
        label "jenkins-cpu"
    }
    stages {
        stage("Build") {
            steps {
	        script {
                    properties([pipelineTriggers([pollSCM('H/5 * * * *')])])
                }
                checkout scm
                sh "make build"
            }
        }
        stage("Tests") {
            steps {
		bash "make api-tests"
                archiveArtifacts artifacts: "roles/api-tests/results/**/*", fingerprint: true
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
