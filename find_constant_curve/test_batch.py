from batch import BatchScript

s = BatchScript()
s.set_job_name("test1")
s.set_reservation("now")
s.set_command("python3 ~/Worm/EffectiveBorromeanWorm/bisection/test.py")
s.set_run_time(100)
s.set_output_name("out")
id1 = s.run_batch()
s.set_job_name("test2")
s.set_dependency(f"afterany:{id1}")
s.run_batch()