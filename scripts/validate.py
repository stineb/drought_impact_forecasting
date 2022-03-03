import sys
import os
import wandb
import numpy as np
sys.path.append(os.getcwd())
from logging import Logger
from shutil import copy2
from os import listdir
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import WandbLogger
from config.config import validate_line_parser
from drought_impact_forecasting.models.EN_model import EN_model
from Data.data_preparation import Earth_net_DataModule
from scripts.callbacks import WandbTest_callback

def main():
    
    configs = validate_line_parser()

    print("Validating experiment {0}".format(configs['run_name']))
    print("Validating model at epoch {0}".format(configs['epoch_to_validate']))

    wandb.login()

    # GPU handling
    # print("GPU count: {0}".format(gpu_count))

    wandb_logger = WandbLogger(entity="eth-ds-lab", project="DIF Testing", offline=True)

    # always use same val_2 data from Data folder
    EN_dataset = Earth_net_DataModule(data_dir = configs['dataset_dir'],
                                     train_batch_size = configs['batch_size'],
                                     val_batch_size = configs['batch_size'],
                                     test_batch_size = configs['batch_size'],
                                     test_set = configs['test_set'],
                                     mesoscale_cut = [39,41])
    
    callbacks = WandbTest_callback(configs['run_name'], configs['epoch_to_validate'], configs['test_set'])

    # setup Trainer
    trainer = Trainer(logger=wandb_logger, callbacks=[callbacks])

    # setup Model
    model = EN_model.load_from_checkpoint(configs['model_path'])
    model.eval()

    # run validation
    trainer.test(model = model, dataloaders = EN_dataset)

    wandb.finish()

if __name__ == "__main__":
    main()
