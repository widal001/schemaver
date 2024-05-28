# About schema versions

## Supported schema change scenarios

- [ ] Supported changes for all properties:
  - [ ] Adding it
  - [ ] Removing it
  - [ ] Changing its validation:
    - [ ] required
    - [ ] type
    - [ ] enum
    - [ ] format
  - [ ] Changing its metadata:
    - [ ] title
    - [ ] description
    - [ ] default
    - [ ] deprecated
    - [ ] readOnly
    - [ ] writeOnly
    - [ ] examples
- [ ] Supported validation changes for objects:
  - [ ] AdditionalProperties
  - [ ] patternProperties
  - [ ] maxProperties
  - [ ] minProperties
  - [ ] dependentRequired
- [ ] Supported validation changes for arrays:
  - [ ] items
  - [ ] prefixItems
  - [ ] maxItems
  - [ ] minItems
  - [ ] contains
  - [ ] uniqueItems
  - [ ] maxContains
  - [ ] minContains
- [ ] Supported validation changes for number and integer:
  - [ ] multipleOf
  - [ ] maximum
  - [ ] exclusiveMaximum
  - [ ] minimum
  - [ ] exclusiveMinimum
- [ ] Supported validation changes for strings:
  - [ ] maxLength
  - [ ] minLength
  - [ ] pattern

> [!NOTE]
> The new versions listed in the tables below is based on the assumption that the previous version was `1-1-1`. This sample version was chosen to highlight which components of the version number:
> - remain unchanged
> - are incremented by one
> - are reset to zero

### Adding a property

The following table maps the update scenarios when a new property is added to a schema with type `object`. The table assumes the old schema's version is `1-1-1`

| Required (now) | Add'l props (before) | Change level | New version |
| -------------- | -------------------- | ------------ | ----------- |
| Optional       | Not allowed          | 🟢 Addition | `1-1-2`     |
| Optional       | Allowed              | 🟡 Revision | `1-2-0`     |
| Required       | Not allowed          | 🔴 Model    | `2-0-0`     |
| Required       | Allowed              | 🟡 Revision | `1-2-0`     |

### Removing a property

The following table maps the update scenarios when a new property is added to a schema with type `object`

| Required (before) | Add'l props (now) | Change level | New version |
| ----------------- | ----------------- | ------------ | ----------- |
| Optional          | Not allowed       | 🟡 Revision | `1-1-0`     |
| Optional          | Allowed           | 🟢 Addition | `1-1-2`     |
| Required          | Not allowed       | 🔴 Model    | `2-0-0`     |
| Required          | Allowed           | 🟢 Addition | `1-1-2`     |

### Adding validation

Adding the following validations to existing props results in a new **Revision**.

| Instance type         | Validation type     | Change level | New version |
| --------------------- | ------------------- | ------------ | ----------- |
| Any                   | `type`              | 🟡 Revision | `1-1-0`     |
| Any                   | `enum`              | 🟡 Revision | `1-1-0`     |
| Any                   | `format`            | 🟡 Revision | `1-1-0`     |
| `array`               | `items`             | 🟡 Revision | `1-1-0`     |
| `array`               | `maxItems`          | 🟡 Revision | `1-1-0`     |
| `array`               | `minItems`          | 🟡 Revision | `1-1-0`     |
| `array`               | `contains`          | 🟡 Revision | `1-1-0`     |
| `array`               | `uniqueItems`       | 🟡 Revision | `1-1-0`     |
| `array`               | `maxContains`       | 🟡 Revision | `1-1-0`     |
| `array`               | `minContains`       | 🟡 Revision | `1-1-0`     |
| `object`              | `maxProperties`     | 🟡 Revision | `1-1-0`     |
| `object`              | `minProperties`     | 🟡 Revision | `1-1-0`     |
| `object`              | `dependentRequired` | 🟡 Revision | `1-1-0`     |
| `integer` or `number` | `multipleOf`        | 🟡 Revision | `1-1-0`     |
| `integer` or `number` | `maximum`           | 🟡 Revision | `1-1-0`     |
| `integer` or `number` | `exclusiveMaximum`  | 🟡 Revision | `1-1-0`     |
| `integer` or `number` | `minimum`           | 🟡 Revision | `1-1-0`     |
| `integer` or `number` | `exclusiveMinimum`  | 🟡 Revision | `1-1-0`     |
| `string`              | `maxLength`         | 🟡 Revision | `1-1-0`     |
| `string`              | `minLength`         | 🟡 Revision | `1-1-0`     |
| `string`              | `pattern`           | 🟡 Revision | `1-1-0`     |

### Removing validation

Removing the following validations to existing props results in a new **Addition**.

| Instance type         | Validation type     | Change level | New version |
| --------------------- | ------------------- | ------------ | ----------- |
| Any                   | `type`              | 🟢 Addition | `1-1-2`     |
| Any                   | `enum`              | 🟢 Addition | `1-1-2`     |
| Any                   | `format`            | 🟢 Addition | `1-1-2`     |
| `array`               | `items`             | 🟢 Addition | `1-1-2`     |
| `array`               | `maxItems`          | 🟢 Addition | `1-1-2`     |
| `array`               | `minItems`          | 🟢 Addition | `1-1-2`     |
| `array`               | `contains`          | 🟢 Addition | `1-1-2`     |
| `array`               | `uniqueItems`       | 🟢 Addition | `1-1-2`     |
| `array`               | `maxContains`       | 🟢 Addition | `1-1-2`     |
| `array`               | `minContains`       | 🟢 Addition | `1-1-2`     |
| `object`              | `maxProperties`     | 🟢 Addition | `1-1-2`     |
| `object`              | `minProperties`     | 🟢 Addition | `1-1-2`     |
| `object`              | `dependentRequired` | 🟢 Addition | `1-1-2`     |
| `integer` or `number` | `multipleOf`        | 🟢 Addition | `1-1-2`     |
| `integer` or `number` | `maximum`           | 🟢 Addition | `1-1-2`     |
| `integer` or `number` | `exclusiveMaximum`  | 🟢 Addition | `1-1-2`     |
| `integer` or `number` | `minimum`           | 🟢 Addition | `1-1-2`     |
| `integer` or `number` | `exclusiveMinimum`  | 🟢 Addition | `1-1-2`     |
| `string`              | `maxLength`         | 🟢 Addition | `1-1-2`     |
| `string`              | `minLength`         | 🟢 Addition | `1-1-2`     |
| `string`              | `pattern`           | 🟢 Addition | `1-1-2`     |

### Modifying validation

Modifying validations can result in a new Model, Revision, or Addition, depending on the type of validation and the nature of the change.

| Validation type    | Change details       | Change level | New version |
| ------------------ | -------------------- | ------------ | ----------- |
| `required`         | Optional to required | 🟡 Revision | `1-2-0`     |
| `required`         | Required to optional | 🟢 Addition | `1-1-2`     |
| `type`             | N/A                  | 🔴 Model    | `2-0-0`     |
| `enum`             | Option(s) added      | 🟢 Addition | `1-1-2`     |
| `enum`             | Option(s) removed    | 🟡 Revision | `1-2-0`     |
| `format`           | N/A                  | 🔴 Model    | `2-0-0`     |
| `maxItems`         | ⬆ Increased max     | 🟢 Addition | `1-1-2`     |
| `maxItems`         | ⬇ Decreased max     | 🟡 Revision | `1-2-0`     |
| `minItems`         | ⬆ Increased min     | 🟡 Revision | `1-2-0`     |
| `minItems`         | ⬇ Decreased min     | 🟢 Addition | `1-1-2`     |
| `uniqueItems`      | False to True        | 🟡 Revision | `1-2-0`     |
| `uniqueItems`      | True to False        | 🟢 Addition | `1-1-2`     |
| `maxContains`      | ⬆ Increased max     | 🟢 Addition | `1-1-2`     |
| `maxContains`      | ⬇ Decreased max     | 🟡 Revision | `1-2-0`     |
| `minContains`      | ⬆ Increased min     | 🟡 Revision | `1-2-0`     |
| `minContains`      | ⬇ Decreased min     | 🟢 Addition | `1-1-2`     |
| `maxProperties`    | ⬆ Increased max     | 🟢 Addition | `1-1-2`     |
| `maxProperties`    | ⬇ Decreased max     | 🟡 Revision | `1-2-0`     |
| `minProperties`    | ⬆ Increased min     | 🟡 Revision | `1-2-0`     |
| `minProperties`    | ⬇ Decreased min     | 🟢 Addition | `1-1-2`     |
| `multipleOf`       | Factor of previous   | 🟢 Addition | `1-1-2`     |
| `multipleOf`       | Has common factor    | 🟡 Revision | `1-2-0`     |
| `multipleOf`       | No common factor     | 🔴 Model    | `2-0-0`     |
| `maximum`          | ⬆ Increased max     | 🟢 Addition | `1-1-2`     |
| `maximum`          | ⬇ Decreased max     | 🟡 Revision | `1-2-0`     |
| `exclusiveMaximum` | ⬆ Increased min     | 🟡 Revision | `1-2-0`     |
| `exclusiveMaximum` | ⬇ Decreased min     | 🟢 Addition | `1-1-2`     |
| `minimum`          | ⬆ Increased max     | 🟢 Addition | `1-1-2`     |
| `minimum`          | ⬇ Decreased max     | 🟡 Revision | `1-2-0`     |
| `exclusiveMinimum` | ⬆ Increased min     | 🟡 Revision | `1-2-0`     |
| `exclusiveMinimum` | ⬇ Decreased min     | 🟢 Addition | `1-1-2`     |
| `maxLength`        | ⬆ Increased max     | 🟢 Addition | `1-1-2`     |
| `maxLength`        | ⬇ Decreased max     | 🟡 Revision | `1-2-0`     |
| `minLength`        | ⬆ Increased min     | 🟡 Revision | `1-2-0`     |
| `minLength`        | ⬇ Decreased min     | 🟢 Addition | `1-1-2`     |
| `pattern`          | Less restrictive     | 🟢 Addition | `1-1-2`     |
| `pattern`          | More restrictive     | 🟡 Revision | `1-2-0`     |

### Modifying metadata

Adding, removing, or changing the following metadata elements results in a new **Addition**

| Metadata type | Change level | New version |
| ------------- | ------------ | ----------- |
| `title`       | 🟢 Addition | `1-1-2`     |
| `description` | 🟢 Addition | `1-1-2`     |
| `default`     | 🟢 Addition | `1-1-2`     |
| `deprecated`  | 🟢 Addition | `1-1-2`     |
| `readOnly`    | 🟢 Addition | `1-1-2`     |
| `writeOnly`   | 🟢 Addition | `1-1-2`     |
| `examples`    | 🟢 Addition | `1-1-2`     |
