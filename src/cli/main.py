#!/usr/bin/env python3

import click
import logging
import sys
from pathlib import Path
import yaml
from typing import Optional, Dict, Any
import json

from ..core.processor import Processor
from ..utils.satellite_utils import setup_logging
from ..api.server import create_app

def load_config(config_path: Optional[str]) -> Dict[Any, Any]:
    """Load configuration from file"""
    if not config_path:
        default_config = Path(__file__).parent.parent.parent / 'config' / 'config.yaml'
        if default_config.exists():
            config_path = str(default_config)
        else:
            return {}
    
    try:
        with open(config_path) as f:
            return yaml.safe_load(f)
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        sys.exit(1)

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug mode')
@click.option('--config', type=click.Path(exists=True), help='Path to config file')
@click.pass_context
def cli(ctx: click.Context, debug: bool, config: Optional[str] = None):
    """Vortx CLI - High-performance geospatial processing engine"""
    ctx.ensure_object(dict)
    log_level = logging.DEBUG if debug else logging.INFO
    setup_logging(log_level)
    
    ctx.obj['config'] = load_config(config)
    ctx.obj['debug'] = debug

@cli.command()
@click.option('--host', default='127.0.0.1', help='The host to bind to')
@click.option('--port', default=5000, help='The port to bind to')
@click.option('--reload/--no-reload', default=False, help='Enable auto-reload')
@click.pass_context
def serve(ctx: click.Context, host: str, port: int, reload: bool):
    """Start the Vortx API server"""
    try:
        app = create_app(config=ctx.obj.get('config', {}))
        click.echo(f"Starting server at http://{host}:{port}")
        app.run(host=host, port=port, reload=reload)
    except Exception as e:
        click.echo(f"Error starting server: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.argument('output_path', type=click.Path())
@click.option('--model', default='default', help='Model to use for processing')
@click.option('--batch-size', default=1, help='Batch size for processing')
@click.option('--gpu/--no-gpu', default=True, help='Use GPU if available')
@click.pass_context
def process(ctx: click.Context, input_path: str, output_path: str, model: str, batch_size: int, gpu: bool):
    """Process satellite data"""
    try:
        processor = Processor(
            model=model,
            config=ctx.obj.get('config', {}),
            use_gpu=gpu,
            batch_size=batch_size
        )
        processor.process_file(
            Path(input_path),
            Path(output_path)
        )
        click.echo(f"Successfully processed {input_path} -> {output_path}")
    except Exception as e:
        click.echo(f"Error during processing: {e}", err=True)
        if ctx.obj.get('debug'):
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)

@cli.command()
@click.pass_context
def version(ctx: click.Context):
    """Show version information"""
    try:
        import pkg_resources
        version = pkg_resources.get_distribution('vortx').version
        info = {
            'version': version,
            'python': sys.version,
            'debug': ctx.obj.get('debug', False),
            'config_loaded': bool(ctx.obj.get('config'))
        }
        click.echo(json.dumps(info, indent=2))
    except Exception as e:
        click.echo(f"Error getting version info: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('--recursive/--no-recursive', default=True, help='Search recursively')
@click.option('--pattern', default='*.tif', help='File pattern to match')
@click.pass_context
def analyze(ctx: click.Context, input_dir: str, recursive: bool, pattern: str):
    """Analyze satellite data directory"""
    try:
        path = Path(input_dir)
        glob_pattern = f"**/{pattern}" if recursive else pattern
        files = list(path.glob(glob_pattern))
        
        click.echo(f"Found {len(files)} files matching pattern '{pattern}'")
        for file in files:
            size_mb = file.stat().st_size / (1024 * 1024)
            click.echo(f"- {file.relative_to(path)} ({size_mb:.1f} MB)")
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--check/--no-check', default=True, help='Check dependencies without installing')
@click.pass_context
def setup(ctx: click.Context, check: bool):
    """Setup and verify environment"""
    try:
        import pkg_resources
        
        click.echo("Checking dependencies...")
        with open(Path(__file__).parent.parent.parent / 'requirements.txt') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        missing = []
        for req in requirements:
            try:
                pkg_resources.require(req)
            except:
                missing.append(req)
        
        if missing:
            click.echo(f"\nMissing {len(missing)} dependencies:")
            for req in missing:
                click.echo(f"- {req}")
            if not check:
                click.echo("\nInstalling missing dependencies...")
                # Implement dependency installation here
        else:
            click.echo("All dependencies are satisfied!")
    except Exception as e:
        click.echo(f"Error during setup: {e}", err=True)
        sys.exit(1)

def main():
    """Main entry point for the CLI"""
    cli(obj={})

if __name__ == '__main__':
    main() 