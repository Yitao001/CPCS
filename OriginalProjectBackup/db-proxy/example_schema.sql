-- ==========================================
-- 示例数据库表结构
-- 仅供参考，请根据您的实际表结构修改
-- ==========================================

-- 创建示例表
CREATE TABLE IF NOT EXISTS talk_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(50) NOT NULL COMMENT '学生ID',
    content TEXT NOT NULL COMMENT '谈话内容',
    created_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX idx_student_id (student_id),
    INDEX idx_created_time (created_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='谈话记录表';

-- 插入测试数据
INSERT INTO talk_record (student_id, content, created_time) VALUES
('S2023001', '今天学习了数学，感觉有点难，特别是几何部分。', '2026-04-01 09:00:00'),
('S2023001', '老师布置了新的作业，我会认真完成的。', '2026-04-02 14:30:00'),
('S2023001', '今天考试了，希望能有个好成绩。', '2026-04-03 16:00:00'),
('S2023002', '我喜欢上体育课，今天跑了800米。', '2026-04-01 10:00:00'),
('S2023002', '和同学相处很好，大家都很友善。', '2026-04-02 15:00:00'),
('S2023003', '最近在读一本有趣的书，讲的是历史故事。', '2026-04-01 11:00:00'),
('S2023003', '周末计划去图书馆看书，顺便复习功课。', '2026-04-02 16:00:00'),
('S2023003', '今天的语文课很有意思，老师讲得很好。', '2026-04-03 17:00:00');
