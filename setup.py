#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 cx_Freeze 的 setup.py 脚本
"""

from cx_Freeze import setup, Executable

setup(
    name="gomoko",
    version="1.0",
    description="ASCII字符五子棋游戏",
    options={
        "build_exe": {
            "packages": [],
            "include_files": [],
            "excludes": ["tkinter"],
        }
    },
    executables=[
        Executable(
            "gobang.py",
            base="Console",
            target_name="gomoko.exe"
        )
    ]
)
