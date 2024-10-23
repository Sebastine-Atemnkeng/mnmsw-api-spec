pipeline {
    agent any

    parameters {
        string(name: 'BRANCH_NAME', defaultValue: 'release', description: 'Enter the branch name (e.g., bugfix)')
    }

    environment {
        registryCredential = 'dockerhub'
        registry = "sebastine/project-tsukinome-${params.BRANCH_NAME}"
        dockerImage = ''
        newVersion = ''  // Declare newVersion here so it's globally accessible
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    checkout([$class: 'GitSCM', branches: [[name: "*/${params.BRANCH_NAME}"]], userRemoteConfigs: [[url: 'https://github.com/Sebastine-Atemnkeng/mnmsw-api-spec.git']]])
                }
            }
        }

        stage('Read Version') {
            steps {
                script {
                    // Read the version from version.txt
                    def version = readFile('version.txt').trim()
                    echo "Current version: ${version}"

                    // Increment version based on commit (can be automated or predefined logic)
                    def newVersion = incrementVersion(version, 'patch') // You can use 'major', 'minor', or 'patch'
                    echo "New version: ${newVersion}"

                    // Write new version back to version.txt
                    writeFile file: 'version.txt', text: newVersion
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                """
            }
        }

        stage('Unit Test') {
            steps {
                sh """
                    . venv/bin/activate
                    pytest --junitxml=test-results.xml
                """
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                        def dockerRepo = "sebastine/project-tsukinome-${params.BRANCH_NAME}:${newVersion}"

                        // Log in to Docker Hub
                        sh "echo \$DOCKERHUB_PASSWORD | docker login -u \$DOCKERHUB_USERNAME --password-stdin"

                        // Build Docker image
                        dockerImage = docker.build("${registry}:${newVersion}")

                        // Push Docker image to the registry
                        dockerImage.push()

                        // Optionally clean up the local Docker image
                        sh "docker rmi ${registry}:${newVersion} || true"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def colorMap = [
                    SUCCESS: 'good',
                    FAILURE: 'danger',
                    UNSTABLE: 'warning'
                ]
                def buildResult = currentBuild.currentResult
                def color = colorMap[buildResult] ?: 'warning'
                slackSend channel: 'jenkinscicd', color: color, message: "*${buildResult}:* Job ${env.JOB_NAME} build ${env.BUILD_NUMBER} \n More info at: ${env.BUILD_URL}"
            }
        }
    }
}

def incrementVersion(String version, String type) {
    def parts = version.tokenize('.')
    def major = parts[0].toInteger()
    def minor = parts[1].toInteger()
    def patch = parts[2].toInteger()

    if (type == 'major') {
        major++
        minor = 0
        patch = 0
    } else if (type == 'minor') {
        minor++
        patch = 0
    } else if (type == 'patch') {
        patch++
    }

    return "${major}.${minor}.${patch}"
}
