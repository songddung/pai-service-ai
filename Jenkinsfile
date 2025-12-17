pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo 'Building Docker image...'
                    // Build once with BUILD_NUMBER tag
                    sh "docker build -t songhyunkwang/pai-service-ai:${BUILD_NUMBER} ."
                    // Add latest tag to the same image
                    sh "docker tag songhyunkwang/pai-service-ai:${BUILD_NUMBER} songhyunkwang/pai-service-ai:latest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                script {
                    echo 'Pushing Docker image to Docker Hub...'
                    // Login to Docker Hub and push images
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                        sh "docker push songhyunkwang/pai-service-ai:${BUILD_NUMBER}"
                        sh "docker push songhyunkwang/pai-service-ai:latest"
                    }
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
            echo "Docker image pushed: songhyunkwang/pai-service-ai:${BUILD_NUMBER}"
        }
        failure {
            echo 'Pipeline failed!'
        }
        always {
            // Cleanup: remove Docker images to save space
            sh "docker rmi songhyunkwang/pai-service-ai:${BUILD_NUMBER} || true"
            sh "docker rmi songhyunkwang/pai-service-ai:latest || true"
            // Remove dangling images (untagged <none> images)
            sh "docker image prune -f || true"
            // Clean workspace
            cleanWs()
        }
    }
}
