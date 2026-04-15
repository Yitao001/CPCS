import mysql.connector
import yaml

# 加载数据库配置
with open('config/database.yml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

db_config = config['mysql']

try:
    # 连接数据库
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    print("数据库连接成功！")
    
    # 测试查询
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM talk_record")
    result = cursor.fetchone()
    print(f"talk_record表中有 {result[0]} 条记录")
    
    # 测试学生ID查询
    test_student_id = "1001"
    cursor.execute("SELECT context, created_time FROM talk_record WHERE student_id = %s LIMIT 5", (test_student_id,))
    test_results = cursor.fetchall()
    print(f"学生ID {test_student_id} 的前5条记录:")
    for row in test_results:
        print(f"时间: {row[1]}, 内容: {row[0][:50]}...")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"数据库操作失败: {str(e)}")