// ============================
// Jenkins Pipeline 配置
// ============================
// 功能：自动拉取代码 → 安装依赖 → 执行测试 → 生成报告 → 失败告警
// 触发方式：定时构建 / Git Push / 手动触发

pipeline {
    agent any

    // ===========================
    // 参数定义（可在 Jenkins 界面手动输入）
    // ===========================
    parameters {
        choice(
            name: 'ENV',
            choices: ['test', 'staging', 'prod'],
            description: '选择运行环境'
        )
        choice(
            name: 'BROWSER',
            choices: ['chrome', 'firefox', 'edge'],
            description: '选择浏览器类型'
        )
        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: '是否使用无头模式'
        )
        choice(
            name: 'TEST_LEVEL',
            choices: ['smoke', 'p0', 'p1', 'regression', 'all'],
            description: '测试级别'
        )
        string(
            name: 'RERUNS',
            defaultValue: '1',
            description: '失败重试次数'
        )
        string(
            name: 'WORKERS',
            defaultValue: '1',
            description: '并行 Worker 数量（pytest-xdist）'
        )
    }

    // ===========================
    // 环境变量
    // ===========================
    environment {
        PYTHON_HOME = 'C:\\Python39'
        PROJECT_DIR = "ui_auto_framework"
        ALLURE_HOME = 'C:\\allure-2.25.0\\bin'
        PATH = "${PYTHON_HOME}\\Scripts;${ALLURE_HOME};${PATH}"
    }

    // ===========================
    // 构建触发（每天早上 9 点 + 手动触发）
    // ===========================
    triggers {
        cron('H 9 * * 1-5')  // 工作日每天 9 点
    }

    // ===========================
    // 构建阶段
    // ===========================
    stages {
        // ---------- 阶段 1: 环境准备 ----------
        stage('环境准备') {
            steps {
                echo "========== 环境准备 =========="
                echo "运行环境: ${ENV}"
                echo "浏览器: ${BROWSER}"
                echo "测试级别: ${TEST_LEVEL}"
                echo "失败重试: ${RERUNS} 次"
                echo "并行数: ${WORKERS}"

                // 确保目录存在
                bat 'if not exist reports\\screenshots mkdir reports\\screenshots'
                bat 'if not exist reports\\html mkdir reports\\html'
            }
        }

        // ---------- 阶段 2: 安装依赖 ----------
        stage('安装依赖') {
            steps {
                echo "========== 安装 Python 依赖 =========="
                bat "${PYTHON_HOME}\\Scripts\\pip install -r ${PROJECT_DIR}\\requirements.txt -q"
            }
        }

        // ---------- 阶段 3: 执行测试 ----------
        stage('执行测试') {
            steps {
                echo "========== 开始执行测试 =========="

                // 构建测试标记参数
                script {
                    TEST_MARK = ""
                    switch (params.TEST_LEVEL) {
                        case 'smoke':
                            TEST_MARK = "-m smoke"
                            break
                        case 'p0':
                            TEST_MARK = "-m p0"
                            break
                        case 'p1':
                            TEST_MARK = "-m p1"
                            break
                        case 'regression':
                            TEST_MARK = "-m regression"
                            break
                        case 'all':
                            TEST_MARK = ""
                            break
                    }

                    // 执行 pytest
                    bat """
                        cd ${PROJECT_DIR}
                        ${PYTHON_HOME}\\Scripts\\pytest tests/ ^
                            --env ${ENV} ^
                            --browser ${BROWSER} ^
                            ${HEADLESS ? '--headless' : ''} ^
                            --reruns ${RERUNS} ^
                            -n ${WORKERS} ^
                            ${TEST_MARK} ^
                            --alluredir=reports/html/results ^
                            --clean-alluredir ^
                            -v ^
                            --tb=short ^
                            2>&1
                    """
                }
            }
            post {
                always {
                    // 收集测试结果 XML
                    junit "${PROJECT_DIR}\\reports\\**\\*.xml" allowEmptyResults: true
                    // 归档失败截图
                    archiveArtifacts artifacts: "${PROJECT_DIR}\\reports\\screenshots\\**\\*", allowEmptyArchive: true
                }
            }
        }

        // ---------- 阶段 4: 生成 Allure 报告 ----------
        stage('生成报告') {
            steps {
                echo "========== 生成 Allure 报告 =========="
                allure includeProperties: false, jdk: '', results: [[path: "${PROJECT_DIR}/reports/html/results"]]
            }
        }

        // ---------- 阶段 5: 清理旧报告 ----------
        stage('历史报告') {
            steps {
                echo "========== 归档历史报告 =========="
                bat """
                    if exist reports\\html\\history (
                        xcopy /Y /I reports\\html\\history reports\\html\\results\\history
                    )
                """
            }
        }
    }

    // ===========================
    // 构建后操作
    // ===========================
    post {
        success {
            echo '✅ 测试全部通过！'
        }
        failure {
            echo '❌ 测试执行失败，请查看 Allure 报告和截图'

            // 发送邮件通知
            emailext(
                subject: "❌ UI自动化测试失败 [${ENV}] - ${currentBuild.currentResult}",
                body: """
                    <h3>UI 自动化测试执行失败</h3>
                    <p><b>环境:</b> ${ENV}</p>
                    <p><b>浏览器:</b> ${BROWSER}</p>
                    <p><b>测试级别:</b> ${TEST_LEVEL}</p>
                    <p><b>构建编号:</b> ${env.BUILD_NUMBER}</p>
                    <p><b>持续时间:</b> ${currentBuild.durationString}</p>
                    <p>请查看 <a href="${env.BUILD_URL}">Jenkins 控制台</a> 和 <a href="${env.BUILD_URL}allure">Allure 报告</a></p>
                """,
                to: 'qa-team@company.com, dev-team@company.com',
                mimeType: 'text/html'
            )
        }
        unstable {
            echo '⚠️ 测试结果不稳定（存在跳过或重试通过的用例）'
        }
        always {
            echo "构建结束: ${currentBuild.currentResult}"
            cleanWs cleanWhenNotBuilt: false, notFailBuild: true
        }
    }
}
