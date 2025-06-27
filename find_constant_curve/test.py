import argparse

parser = argparse.ArgumentParser(description = "Bisection find constant curve")
subparsers = parser.add_subparsers(help="Sub-command help", required = True)
start_parser = subparsers.add_parser("start", help="Start bisection")
step_parser = subparsers.add_parser("step", help="Bisection step")


start_parser.add_argument("-p", "--parameters", help="Path to parameter file", required = True)
step_parser.add_argument("--sim_folder", help="Path to the sim folder", required = True)
step_parser.add_argument("--k_chi", type=int, help="Which chi id the step corresponds to", required=True)

args = parser.parse_args()

print(args.k_chi)