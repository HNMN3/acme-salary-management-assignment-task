import { Alert, Button, Stack, Text } from "@mantine/core";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <Alert color="red" title="Something went wrong">
      <Stack gap="sm" align="flex-start">
        <Text size="sm">{message}</Text>
        {onRetry && (
          <Button size="xs" variant="outline" color="red" onClick={onRetry}>
            Retry
          </Button>
        )}
      </Stack>
    </Alert>
  );
}
