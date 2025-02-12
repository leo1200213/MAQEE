# coding=utf-8
# Copyright 2022 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Swin Transformer model configuration"""

from collections import OrderedDict
from typing import Mapping

from packaging import version

from transformers.configuration_utils import PretrainedConfig
from transformers.onnx import OnnxConfig
from transformers.utils import logging

logger = logging.get_logger(__name__)

SWIN_PRETRAINED_CONFIG_ARCHIVE_MAP = {
    "microsoft/swin-tiny-patch4-window7-224": (
        "https://huggingface.co/microsoft/swin-tiny-patch4-window7-224/resolve/main/config.json"
    ),
    # See all Swin models at https://huggingface.co/models?filter=swin
    # microsoft/swin-base-patch4-window7-224
}


class SwinConfig(PretrainedConfig):
    r"""
    This is the configuration class to store the configuration of a [`SwinModel`]. It is used to instantiate a Swin
    model according to the specified arguments, defining the model architecture. Instantiating a configuration with the
    defaults will yield a similar configuration to that of the Swin
    [microsoft/swin-tiny-patch4-window7-224](https://huggingface.co/microsoft/swin-tiny-patch4-window7-224)
    architecture.

    Configuration objects inherit from [`PretrainedConfig`] and can be used to control the model outputs. Read the
    documentation from [`PretrainedConfig`] for more information.

    Args:
        image_size (`int`, *optional*, defaults to 224):
            The size (resolution) of each image.
        patch_size (`int`, *optional*, defaults to 4):
            The size (resolution) of each patch.
        num_channels (`int`, *optional*, defaults to 3):
            The number of input channels.
        embed_dim (`int`, *optional*, defaults to 96):
            Dimensionality of patch embedding.
        depths (`list(int)`, *optional*, defaults to [2, 2, 6, 2]):
            Depth of each layer in the Transformer encoder.
        num_heads (`list(int)`, *optional*, defaults to [3, 6, 12, 24]):
            Number of attention heads in each layer of the Transformer encoder.
        window_size (`int`, *optional*, defaults to 7):
            Size of windows.
        mlp_ratio (`float`, *optional*, defaults to 4.0):
            Ratio of MLP hidden dimensionality to embedding dimensionality.
        qkv_bias (`bool`, *optional*, defaults to True):
            Whether or not a learnable bias should be added to the queries, keys and values.
        hidden_dropout_prob (`float`, *optional*, defaults to 0.0):
            The dropout probability for all fully connected layers in the embeddings and encoder.
        attention_probs_dropout_prob (`float`, *optional*, defaults to 0.0):
            The dropout ratio for the attention probabilities.
        drop_path_rate (`float`, *optional*, defaults to 0.1):
            Stochastic depth rate.
        hidden_act (`str` or `function`, *optional*, defaults to `"gelu"`):
            The non-linear activation function (function or string) in the encoder. If string, `"gelu"`, `"relu"`,
            `"selu"` and `"gelu_new"` are supported.
        use_absolute_embeddings (`bool`, *optional*, defaults to False):
            Whether or not to add absolute position embeddings to the patch embeddings.
        patch_norm (`bool`, *optional*, defaults to True):
            Whether or not to add layer normalization after patch embedding.
        initializer_range (`float`, *optional*, defaults to 0.02):
            The standard deviation of the truncated_normal_initializer for initializing all weight matrices.
        layer_norm_eps (`float`, *optional*, defaults to 1e-12):
            The epsilon used by the layer normalization layers.
        encoder_stride (`int`, `optional`, defaults to 32):
            Factor to increase the spatial resolution by in the decoder head for masked image modeling.
        out_features (`List[str]`, *optional*):
            If used as backbone, list of features to output. Can be any of `"stem"`, `"stage1"`, `"stage2"`, etc.
            (depending on how many stages the model has). Will default to the last stage if unset.

    Example:

    ```python
    >>> from transformers import SwinConfig, SwinModel

    >>> # Initializing a Swin microsoft/swin-tiny-patch4-window7-224 style configuration
    >>> configuration = SwinConfig()

    >>> # Initializing a model (with random weights) from the microsoft/swin-tiny-patch4-window7-224 style configuration
    >>> model = SwinModel(configuration)

    >>> # Accessing the model configuration
    >>> configuration = model.config
    ```"""
    model_type = "swin"

    attribute_map = {
        "num_attention_heads": "num_heads",
        "num_hidden_layers": "num_layers",
    }

    def __init__(
        self,
        image_size=224,
        patch_size=4,
        num_channels=3,
        embed_dim=96,
        depths=[2, 2, 6, 2],
        num_heads=[3, 6, 12, 24],
        window_size=7,
        mlp_ratio=4.0,
        qkv_bias=True,
        hidden_dropout_prob=0.0,
        attention_probs_dropout_prob=0.0,
        drop_path_rate=0.1,
        hidden_act="gelu",
        use_absolute_embeddings=False,
        patch_norm=True,
        initializer_range=0.02,
        layer_norm_eps=1e-5,
        encoder_stride=32,
        out_features=None,
        num_early_exits='[0,1,6,1]',
        position_exits='[[],[2],[3,6,9,12,15,18],[1]]',
        exit_strategy='confidence',
        train_strategy='normal',
        highway_type='linear',
        loss_coefficient=0.3,
        homo_loss_coefficient=0.01,
        hete_loss_coefficient=0.01,
        output_hidden_states=False,
        threshold = None,
        feature_loss_coefficient=0.0,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.image_size = image_size
        self.patch_size = patch_size
        self.num_channels = num_channels
        self.embed_dim = embed_dim
        self.depths = depths
        self.num_layers = len(depths)
        self.num_heads = num_heads
        self.window_size = window_size
        self.mlp_ratio = mlp_ratio
        self.qkv_bias = qkv_bias
        self.hidden_dropout_prob = hidden_dropout_prob
        self.attention_probs_dropout_prob = attention_probs_dropout_prob
        self.drop_path_rate = drop_path_rate
        self.hidden_act = hidden_act
        self.use_absolute_embeddings = use_absolute_embeddings
        self.path_norm = patch_norm
        self.layer_norm_eps = layer_norm_eps
        self.initializer_range = initializer_range
        self.encoder_stride = encoder_stride
        self.feature_loss_coefficient = feature_loss_coefficient
        # we set the hidden_size attribute in order to make Swin work with VisionEncoderDecoderModel
        # this indicates the channel dimension after the last stage of the model
        self.hidden_size = int(embed_dim * 2 ** (len(depths) - 1))
        self.stage_names = ["stem"] + [f"stage{idx}" for idx in range(1, len(depths) + 1)]
        if out_features is not None:
            if not isinstance(out_features, list):
                raise ValueError("out_features should be a list")
            for feature in out_features:
                if feature not in self.stage_names:
                    raise ValueError(
                        f"Feature {feature} is not a valid feature name. Valid names are {self.stage_names}"
                    )
        self.out_features = out_features
        
        self.num_early_exits = num_early_exits
        self.position_exits = position_exits
        self.exit_strategy = exit_strategy
        self.train_strategy = train_strategy
        self.highway_type = highway_type
        self.threshold = threshold
        self.loss_coefficient = loss_coefficient
        self.homo_loss_coefficient = homo_loss_coefficient
        self.hete_loss_coefficient = hete_loss_coefficient
        self.output_hidden_states = output_hidden_states
        

class SwinOnnxConfig(OnnxConfig):

    torch_onnx_minimum_version = version.parse("1.11")

    @property
    def inputs(self) -> Mapping[str, Mapping[int, str]]:
        return OrderedDict(
            [
                ("pixel_values", {0: "batch", 1: "num_channels", 2: "height", 3: "width"}),
            ]
        )

    @property
    def atol_for_validation(self) -> float:
        return 1e-4
