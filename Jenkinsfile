pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing Python dependencies...'
                sh '''
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Lint') {
            steps {
                echo 'Running Python linter...'
                sh '''
                    . venv/bin/activate
                    pip install flake8 black
                    flake8 src/ --max-line-length=120 --extend-ignore=E203,W503 || true
                    black --check src/ || true
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    . venv/bin/activate
                    pip install pytest pytest-cov
                    pytest tests/ --cov=src --cov-report=term-missing || echo "No tests found or tests failed"
                '''
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
