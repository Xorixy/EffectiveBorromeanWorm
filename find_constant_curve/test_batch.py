from batch import BatchScript

s = BatchScript()
s.set_job_name("test1")
s.set_reservation("now")
s.set_command("python3 ~/Worm/EffectiveBorromeanWorm/bisection/test_open.py")
s.set_run_time(100)
s.set_output_name("out")
s.run_batch()
s.run_batch()
s.run_batch()
s.run_batch()
s.run_batch()