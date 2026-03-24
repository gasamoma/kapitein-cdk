# Contributing to kapitein-cdk

## Adding a New Construct

1. Create a new file in `kapitein_cdk/` (e.g. `my_construct.py`)
2. Implement your construct extending `Construct`
3. Export it from `kapitein_cdk/__init__.py`
4. Add an entry to `CHANGELOG.md`

### Construct conventions

- Class name ends in `Construct` (e.g. `MyFeatureConstruct`)
- All constructor parameters have type hints and docstrings
- Expose created resources as `@property` methods
- Default `removal_policy` to `RemovalPolicy.RETAIN` for stateful resources
- No hardcoded account IDs, region names, or project-specific values

### Example skeleton

```python
from aws_cdk import RemovalPolicy
from constructs import Construct

class MyConstruct(Construct):
    """One-line description.

    Longer description of what this bundles and why.
    """

    def __init__(self, scope: Construct, construct_id: str,
                 my_param: str,
                 removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # ... create resources ...

    @property
    def my_resource(self):
        """The created resource."""
        return self._my_resource
```

## Versioning

This project uses [Semantic Versioning](https://semver.org/):
- **Patch** (`0.1.x`) — bug fixes, no API changes
- **Minor** (`0.x.0`) — new constructs or backwards-compatible additions
- **Major** (`x.0.0`) — breaking changes to existing construct APIs

## Submitting a PR

1. Fork the repo and create a branch from `main`
2. Make your changes
3. Update `CHANGELOG.md`
4. Open a pull request with a clear description

## License

By contributing, you agree your contributions will be licensed under Apache 2.0.
