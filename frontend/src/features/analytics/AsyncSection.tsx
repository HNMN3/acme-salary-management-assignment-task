import { Card, Text, Title } from "@mantine/core";
import type { ReactNode } from "react";

import { ErrorState } from "../../shared/components/ErrorState";
import { LoadingState } from "../../shared/components/LoadingState";
import type { AsyncData } from "../../shared/hooks/useAsyncData";

interface AsyncSectionProps<T> {
  title: string;
  state: AsyncData<T>;
  isEmpty?: (data: T) => boolean;
  children: (data: T) => ReactNode;
}

export function AsyncSection<T>({
  title,
  state,
  isEmpty,
  children,
}: AsyncSectionProps<T>) {
  let body: ReactNode;
  if (state.error) {
    body = <ErrorState message={state.error.message} onRetry={state.reload} />;
  } else if (state.data === undefined) {
    body = <LoadingState label={`Loading ${title}`} />;
  } else if (isEmpty?.(state.data)) {
    body = (
      <Text c="dimmed" ta="center" py="xl">
        No data for the selected filters.
      </Text>
    );
  } else {
    body = children(state.data);
  }

  return (
    <Card withBorder component="section" aria-label={title}>
      <Title order={4} mb="sm">
        {title}
      </Title>
      {body}
    </Card>
  );
}
