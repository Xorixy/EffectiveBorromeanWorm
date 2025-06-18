from batch import BatchScript

s = BatchScript()
s.set_job_name("test")
s.set_reservation("now")
s.set_command("python3 ~/Worm/EffectiveBorromeanWorm/bisection/test.py")
s.set_run_time(100)
s.set_output_name("~/Worm/EffectiveBorromeanWorm/bisection")
print(s.run_batch())