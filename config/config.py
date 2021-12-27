import argparse
import os
import json


def train_line_parser(cfg):
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-tl', '--training_loss', type=str, default='l2', choices=['l1','l2','Huber'], help='loss function used for training')
    parser.add_argument('-bs', '--batch_size', type=int, default=None, help='batch size')
    parser.add_argument('-bm', '--big_memory', type=str, default=None, help='big memory or small: t = ture, f = false')
    parser.add_argument('-nl', '--num_layers', type=int, default=None, help='number of layers')
    parser.add_argument('-ln', '--layer_normalization', type=str, default=None, help='òayer normalization: t = ture, f = false')
    parser.add_argument('-ft', '--future_training', type=int, default=None, help='future steps for training')
    parser.add_argument('-lr', '--learining_rate' , type=float, default=None, help='starting learining rate')
    parser.add_argument('-e',  '--epochs', type=int, default=200, help='training epochs')
    parser.add_argument('-bf', '--baseline_function', type=str, default=None, choices=['mean_cube', 'last_frame'], help='baseline function')
    parser.add_argument('-pd', '--pickle_dir', type=str, default=None, help='directory with the desired pickle files')
    args = parser.parse_args()

    if args.batch_size is not None:
        cfg["training"]["train_batch_size"] = args.batch_size
        cfg["training"]["val_1_batch_size"] = args.batch_size
        cfg["training"]["val_2_batch_size"] = args.batch_size

    if args.big_memory is not None:
        if args.big_memory == "y" or args.big_memory == "Y" or args.big_memory == "T" or args.big_memory == "t":
            cfg["model"]["big_mem"] = True
        elif args.big_memory == "n" or args.big_memory == "N" or args.big_memory == "f" or args.big_memory == "F":
            cfg["model"]["big_mem"] = False
    
    if args.layer_normalization is not None:
        if args.layer_normalization == "y" or args.layer_normalization == "Y" or args.layer_normalization == "T" or args.layer_normalization == "t":
            cfg["model"]["layer_norm"] = True
        elif args.layer_normalization == "n" or args.layer_normalization == "N" or args.layer_normalization == "f" or args.layer_normalization == "F":
            cfg["model"]["layer_norm"] = False
    
    if args.num_layers is not None:
        cfg["model"]["n_layers"] = args.num_layers

    if args.future_training is not None:
        cfg["model"]["future_training"] = args.future_training

    if args.learining_rate is not None:
        cfg["training"]["start_learn_rate"] = args.learining_rate

    if args.epochs is not None:
        cfg["training"]["epochs"] = args.epochs

    if args.baseline_function is not None:
        cfg["model"]["baseline"] = args.baseline_function

    if args.training_loss is not None:
        cfg["training"]["training_loss"] = args.training_loss
        
    if args.pickle_dir is not None:
        cfg["data"]["pickle_dir"] = args.pickle_dir
    
    return cfg

def validate_line_parser():
    parser = argparse.ArgumentParser(
        add_help=True,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('-cp','--check_point_path', type=str, default=None, help='checkpoint file to validate. Note: either use --checkpoint or --run_name, not both')
    parser.add_argument('-rn','--run_name', type=str, default=None, help='wandb run name to validate. Note: either use --checkpoint or --run_name, not bot')
    parser.add_argument('-bs','--batch_size', type=int, default=4, help='batch size')
    parser.add_argument('-vd','--validation_dataset', type=int, default=None, help='Filepath to the pickle folder of the validation set')
    parser.add_argument('-test','--use_real_test_set', action="store_true", help='If present we use the real test set!')
    parser.add_argument('-e','--epoch_to_validate', type=int, default=-1, help='model epoch to test/validate')
    args = parser.parse_args()

    if args.run_name is not None and args.check_point_path is not None:
        raise ValueError("Either use --checkpoint or --run_name, not bot")

    if args.run_name is not None and args.check_point_path is None:
        dir_path = find_dir_path(args.run_name)
        model_path = os.path.join(dir_path, "files", "runtime_model")
        models = os.listdir(model_path)
        models.sort()
        model_path = os.path.join(model_path , models[args.epoch_to_validate])
        if args.validation_dataset == None:
            cfg = json.load(open(os.path.join(dir_path, "files", "Training.json"), 'r'))
            dataset_dir = cfg["data"]["pickle_dir"]
        else:
            dataset_dir = args.validation_dataset
    
    if args.run_name is None and args.check_point_path is not None:
        model_path = args.check_point_path
        if args.validation_dataset == None:
            raise ValueError("When using a checkpoint outside of a folder one must specify the dataset_directory")
        else:
            dataset_dir = args.validation_dataset
    configs = dict(
        model_path = model_path,
        dataset_dir = dataset_dir,
        run_name = args.run_name,
        epoch_to_validate = args.epoch_to_validate,
        batch_size = args.batch_size,
        use_real_test_set = args.use_real_test_set
    )
    return configs

def find_dir_path(wandb_name):
    dir_path = os.path.join(os.getcwd(), "wandb")

    runs = []
    for path, subdirs, files in os.walk(dir_path):
        for dir_ in subdirs:
            # Ignore any licence, progress, etc. files
            if os.path.isfile(os.path.join(dir_path,dir_, "files", "run_name.txt")):
                with open(os.path.join(dir_path,dir_, "files",  "run_name.txt"),'r') as f:
                    if (f.read() == wandb_name):
                        return os.path.join(dir_path,dir_)
    raise ValueError("The name doesn't exist.")


def read_config(path):
    cfg = json.load(open(path, 'r'))
    return cfg