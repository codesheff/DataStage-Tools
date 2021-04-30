select start_time,  cast(t1.stmt_text as varchar(1024)) test1 from db2inst1.STMT_STEMON1 t1 order by t1.START_TIME desc

