const API_BASE = window.location.origin;
const API_KEY = 'CPCS_test_API_key';

document.addEventListener('DOMContentLoaded', () => {
    console.log('页面加载完成，初始化...');
    console.log('API 地址:', API_BASE);
    console.log('API Key:', API_KEY);
    initTabs();
    loadJobs();
});

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

function showLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'flex';
}

function hideLoading() {
    const loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';
}

async function apiRequest(url, options = {}) {
    try {
        console.log(`API 请求: ${API_BASE}${url}`, options);
        const response = await fetch(`${API_BASE}${url}`, {
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY,
                ...options.headers
            },
            ...options
        });

        console.log(`API 响应状态: ${response.status}`);
        const data = await response.json();
        console.log('API 响应数据:', data);
        return data;
    } catch (error) {
        console.error('API 请求失败:', error);
        throw error;
    }
}

async function parseResume() {
    const studentId = document.getElementById('studentId')?.value;
    const resumeContent = document.getElementById('resumeContent')?.value;

    if (!studentId || !resumeContent) {
        alert('请填写学生ID和简历内容');
        return;
    }

    showLoading();
    try {
        console.log('解析简历...');
        const result = await apiRequest('/parse-resume', {
            method: 'POST',
            body: JSON.stringify({
                student_id: studentId,
                resume_content: resumeContent
            })
        });

        console.log('解析结果:', result);
        if (result.status === 'success' || result.status === 'ok') {
            renderStudentProfile(result.data);
        } else {
            alert('解析失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('解析异常:', error);
        alert('解析失败\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

function renderStudentProfile(data) {
    const container = document.getElementById('studentProfileContent');
    if (!container) return;

    let profile;
    if (typeof data === 'string') {
        try {
            profile = JSON.parse(data);
        } catch (e) {
            profile = { raw: data };
        }
    } else {
        profile = data;
    }

    let html = '';
    
    if (profile.raw) {
        html = `<pre style="white-space: pre-wrap;">${profile.raw}</pre>`;
    } else {
        html = `
            <div class="result-section">
                <h3>基本信息</h3>
                <p><strong>姓名:</strong> ${profile.name || '未填写'}</p>
                <p><strong>专业:</strong> ${profile.major || '未填写'}</p>
                <p><strong>学历:</strong> ${profile.education || '未填写'}</p>
            </div>
            <div class="result-section">
                <h3>评分</h3>
                <p><strong>完整度:</strong> ${profile.completeness_score || 0} 分</p>
                <p><strong>竞争力:</strong> ${profile.competitiveness_score || 0} 分</p>
            </div>
            <div class="result-section">
                <h3>专业技能</h3>
                <div>${(profile.professional_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('')}</div>
            </div>
            <div class="result-section">
                <h3>证书</h3>
                <div>${(profile.certificates || []).map(c => `<span class="certificate-tag">${c}</span>`).join('')}</div>
            </div>
            <div class="result-section">
                <h3>能力评分 (1-10)</h3>
                <ul style="padding-left: 20px;">
                    <li>创新能力: ${profile.innovation_ability || '-'}</li>
                    <li>学习能力: ${profile.learning_ability || '-'}</li>
                    <li>抗压能力: ${profile.stress_resistance || '-'}</li>
                    <li>沟通能力: ${profile.communication_ability || '-'}</li>
                    <li>实习能力: ${profile.internship_ability || '-'}</li>
                </ul>
            </div>
        `;
    }

    container.innerHTML = html;
    document.getElementById('studentProfile').style.display = 'block';
}

async function searchJobs() {
    const keyword = document.getElementById('jobSearch')?.value;
    if (!keyword) {
        alert('请输入搜索关键词');
        return;
    }

    showLoading();
    try {
        const result = await apiRequest(`/jobs/search?keyword=${encodeURIComponent(keyword)}`);
        if (result.status === 'success' || result.status === 'ok') {
            renderJobList(result.data);
        } else {
            alert('搜索失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('搜索异常:', error);
        alert('搜索失败\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function loadJobs() {
    showLoading();
    try {
        const result = await apiRequest('/jobs');
        console.log('岗位列表结果:', result);
        if (result.status === 'success' || result.status === 'ok') {
            renderJobList(result.data);
        } else {
            alert('加载岗位列表失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('加载岗位列表异常:', error);
        alert('加载岗位列表失败，请确保 API 服务已启动\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

function renderJobList(jobs) {
    const container = document.getElementById('jobList');
    if (!container) return;
    
    console.log('渲染岗位列表:', jobs);
    container.innerHTML = jobs.map(job => `
        <div class="job-item" onclick="showJobDetail('${job.job_name}')">
            <div class="job-name">${job.job_name}</div>
            <div class="job-category">${job.company_name || '未知公司'}</div>
            <div class="job-category">${job.salary_range || '薪资面议'}</div>
        </div>
    `).join('');
}

async function showJobDetail(jobName) {
    showLoading();
    try {
        const result = await apiRequest(`/jobs/${encodeURIComponent(jobName)}`);
        console.log('岗位详情结果:', result);
        if (result.status === 'success' || result.status === 'ok') {
            renderJobDetail(result.data);
            const detail = document.getElementById('jobDetail');
            if (detail) detail.style.display = 'block';
        } else {
            alert('加载岗位详情失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('加载岗位详情异常:', error);
        alert('加载岗位详情失败\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

function renderJobDetail(job) {
    const container = document.getElementById('jobDetailContent');
    if (!container) return;
    
    container.innerHTML = `
        <div class="job-detail-section">
            <h3>岗位名称</h3>
            <p style="font-size: 1.2rem; color: #333;">${job.job_name}</p>
        </div>
        <div class="job-detail-section">
            <h3>公司名称</h3>
            <p>${job.company_name || '-'}</p>
        </div>
        <div class="job-detail-section">
            <h3>所属行业</h3>
            <p>${job.industry || '-'}</p>
        </div>
        <div class="job-detail-section">
            <h3>薪资范围</h3>
            <p>${job.salary_range || '面议'}</p>
        </div>
        <div class="job-detail-section">
            <h3>工作地址</h3>
            <p>${job.address || '-'}</p>
        </div>
        <div class="job-detail-section">
            <h3>职位描述</h3>
            <p style="white-space: pre-wrap;">${job.description || '-'}</p>
        </div>
    `;
}

async function generateCareerReport() {
    const studentId = document.getElementById('reportStudentId')?.value;
    const studentInfo = document.getElementById('reportStudentInfo')?.value;
    const targetJob = document.getElementById('reportTargetJob')?.value;

    if (!studentId || !studentInfo || !targetJob) {
        alert('请填写完整信息');
        return;
    }

    showLoading();
    try {
        console.log('生成职业发展报告...');
        const result = await apiRequest('/career-report', {
            method: 'POST',
            body: JSON.stringify({
                student_id: studentId,
                student_info: studentInfo,
                job_name: targetJob
            })
        });

        console.log('报告结果:', result);
        if (result.status === 'success' || result.status === 'ok') {
            renderCareerReport(result.data);
        } else {
            alert('生成报告失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('生成报告异常:', error);
        alert('生成报告失败\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

function renderCareerReport(data) {
    const container = document.getElementById('careerReportContent');
    if (!container) return;

    let report;
    if (typeof data === 'string') {
        try {
            report = JSON.parse(data);
        } catch (e) {
            report = { raw: data };
        }
    } else {
        report = data;
    }

    let html = '';
    
    if (report.raw) {
        html = `<pre style="white-space: pre-wrap;">${report.raw}</pre>`;
    } else {
        html = `
            <div class="result-section">
                <h3>${report.title || '职业发展报告'}</h3>
                <p><strong>生成时间:</strong> ${report.created_time || ''}</p>
            </div>
            <div class="result-section">
                <h3>报告内容</h3>
                <pre style="white-space: pre-wrap; background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">${JSON.stringify(report, null, 2)}</pre>
            </div>
        `;
    }

    container.innerHTML = html;
    document.getElementById('careerReport').style.display = 'block';
}

async function exportReport(format) {
    const studentId = document.getElementById('reportStudentId')?.value;
    if (!studentId) {
        alert('请输入学生ID');
        return;
    }

    showLoading();
    try {
        const result = await apiRequest('/export-report', {
            method: 'POST',
            body: JSON.stringify({
                student_id: studentId,
                format: format
            })
        });

        if (result.status === 'success' || result.status === 'ok') {
            alert(`导出成功！\n\n${result.data}`);
        } else {
            alert('导出失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('导出异常:', error);
        alert('导出失败\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

function handleChatKeypress(event) {
    if (event.key === 'Enter') {
        sendChat();
    }
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const message = input?.value.trim();

    if (!message) return;

    addChatMessage('user', message);
    input.value = '';

    showLoading();
    try {
        console.log('发送聊天请求...');
        const result = await apiRequest('/chat', {
            method: 'POST',
            body: JSON.stringify({ message })
        });

        console.log('聊天响应:', result);
        if (result.status === 'success' || result.status === 'ok') {
            addChatMessage('assistant', result.data);
        } else {
            addChatMessage('assistant', '抱歉，请求失败: ' + (result.message || '未知错误'));
        }
    } catch (error) {
        console.error('聊天请求异常:', error);
        addChatMessage('assistant', '抱歉，请求失败，请确保 API 服务已启动。\n错误: ' + error.message);
    } finally {
        hideLoading();
    }
}

function addChatMessage(role, content) {
    const container = document.getElementById('chatMessages');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;
    messageDiv.textContent = content;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}
